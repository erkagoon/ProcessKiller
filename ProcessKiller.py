import psutil
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import operator
from collections import defaultdict

# Stocker les processus
processes = defaultdict(list)

def get_processes():
    # Effacer le dictionnaire des processus précédents
    for key in processes.keys():
        del processes[key][:]

    # Récupérer les processus actuels
    for proc in psutil.process_iter(['pid', 'name']):
        processes[proc.info['name']].append(proc.info['pid'])

def update_process_list():
    # Effacer tous les éléments existants dans la liste
    tree.delete(*tree.get_children())

    # Ajouter les processus à la treeview
    for name, pids in processes.items():
        tree.insert('', 'end', values=(len(pids), name, "Kill"))

def sortby(tree, col, descending):
    """Fonction pour trier les données lorsqu'une colonne est cliquée."""
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    
    # Si la donnée est un nombre, convertir en int
    try:
        data = [(int(item), child) if item.isdigit() else (item, child) for item, child in data]
    except ValueError:
        pass

    # Trier les données
    data.sort(reverse=descending, key=operator.itemgetter(0))

    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)

    # Inverser l'ordre la prochaine fois
    tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))

def kill_process(event):
    # Vérifier si l'utilisateur a cliqué sur la colonne "Kill"
    if tree.identify_column(event.x) == '#3':
        # Récupérer le nom du processus sélectionné
        item = tree.identify_row(event.y)
        name = tree.item(item, 'values')[1]

        # Tuer tous les processus avec ce nom
        success = True
        for pid in processes[name]:
            try:
                p = psutil.Process(int(pid))
                p.terminate()
            except psutil.NoSuchProcess:
                success = False
            except psutil.AccessDenied:
                success = False

        if success:
            messagebox.showinfo("Succès", f"Tous les processus '{name}' ont été tués avec succès")
        else:
            messagebox.showerror("Erreur", f"Impossible de tuer tous les processus '{name}'")

        # Mettre à jour la liste des processus
        get_processes()
        update_process_list()

def check_cursor(event):
    if tree.identify_column(event.x) == '#3':
        tree.config(cursor='hand2')
    else:
        tree.config(cursor='')

# Créer la fenêtre principale
root = tk.Tk()
root.title("Liste des processus")

# Créer une treeview pour afficher les processus
tree = ttk.Treeview(root, columns=('Nombre', 'Nom', 'Kill'), show='headings')
tree.heading('Nombre', text='Nombre', command=lambda: sortby(tree, 'Nombre', 0))
tree.heading('Nom', text='Nom du processus', command=lambda: sortby(tree, 'Nom', 0))
tree.heading('Kill', text='Tuer le processus')
tree.pack()

# Associer un événement de clic de souris à la treeview
tree.bind('<Button-1>', kill_process)

# Associer un événement de mouvement de la souris à la treeview
tree.bind('<Motion>', check_cursor)

# Créer un bouton pour mettre à jour la liste des processus
button = tk.Button(root, text="Mettre à jour la liste des processus", command=update_process_list)
button.pack()

# Récupérer les processus une première fois
get_processes()

# Mettre à jour la liste des processus
update_process_list()

# Lancer l'interface graphique
root.mainloop()
