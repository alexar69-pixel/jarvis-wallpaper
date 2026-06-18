import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import asyncio
import websockets
import json
from config_manager import load_config, save_config

class JarvisSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis Backend Settings")
        self.root.geometry("500x650")
        self.config = load_config()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_general = ttk.Frame(self.notebook)
        self.tab_shortcuts = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_general, text='General')
        self.notebook.add(self.tab_shortcuts, text='Atajos (Shortcuts)')
        
        self.build_general_tab()
        self.build_shortcuts_tab()
        
        # Save Button at the bottom
        ttk.Button(root, text="Guardar Toda la Configuración", command=self.save_all).pack(pady=10)

    def build_general_tab(self):
        parent = self.tab_general
        # Titulo
        ttk.Label(parent, text="Configuración de Motores (Brain)", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Proveedor
        ttk.Label(parent, text="Motor Activo:").pack(anchor="w", padx=20)
        self.provider_var = tk.StringVar(value=self.config.get("provider", "openclaw"))
        providers = [("OpenClaw (Local)", "openclaw"), ("Google Gemini", "gemini"), ("OpenAI (ChatGPT)", "openai")]
        for text, mode in providers:
            ttk.Radiobutton(parent, text=text, variable=self.provider_var, value=mode).pack(anchor="w", padx=30)
            
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        # API Keys
        ttk.Label(parent, text="Gemini API Key:").pack(anchor="w", padx=20)
        self.gemini_entry = ttk.Entry(parent, width=50)
        self.gemini_entry.insert(0, self.config.get("gemini_api_key", ""))
        self.gemini_entry.pack(padx=20, pady=5)
        
        ttk.Label(parent, text="OpenAI API Key:").pack(anchor="w", padx=20)
        self.openai_entry = ttk.Entry(parent, width=50)
        self.openai_entry.insert(0, self.config.get("openai_api_key", ""))
        self.openai_entry.pack(padx=20, pady=5)
        
        ttk.Label(parent, text="OpenClaw Local URL:").pack(anchor="w", padx=20)
        self.openclaw_entry = ttk.Entry(parent, width=50)
        self.openclaw_entry.insert(0, self.config.get("openclaw_url", "http://127.0.0.1:18789/v1/chat/completions"))
        self.openclaw_entry.pack(padx=20, pady=5)
        
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        # Voz y Wake Word
        ttk.Label(parent, text="Palabra de Activación (Wake Word):").pack(anchor="w", padx=20)
        self.wake_entry = ttk.Entry(parent, width=20)
        self.wake_entry.insert(0, self.config.get("wake_word", "jarvis"))
        self.wake_entry.pack(anchor="w", padx=20, pady=5)

        ttk.Label(parent, text="Ubicación (Clima):").pack(anchor="w", padx=20)
        self.loc_entry = ttk.Entry(parent, width=30)
        self.loc_entry.insert(0, self.config.get("location", "Madrid"))
        self.loc_entry.pack(anchor="w", padx=20, pady=5)
        
        # Tema Visual
        ttk.Label(parent, text="Tema Visual (Interfaz):").pack(anchor="w", padx=20)
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(parent, textvariable=self.theme_var, state="readonly", values=["theme-gold", "theme-matrix", "theme-cyan"])
        self.theme_combo.set(self.config.get("theme", "theme-gold"))
        self.theme_combo.pack(anchor="w", padx=20, pady=5)

    def build_shortcuts_tab(self):
        parent = self.tab_shortcuts
        ttk.Label(parent, text="Gestión de Atajos Rápidos", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Treeview to list shortcuts
        columns = ('name', 'path')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        self.tree.heading('name', text='Nombre')
        self.tree.heading('path', text='Ruta / Comando')
        self.tree.column('name', width=120)
        self.tree.column('path', width=300)
        self.tree.pack(padx=20, pady=10, fill='x')
        
        self.shortcuts = self.config.get("shortcuts", [])
        self.refresh_tree()
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Añadir", command=self.add_shortcut).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.remove_shortcut).pack(side='left', padx=5)

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for sc in self.shortcuts:
            self.tree.insert('', 'end', values=(sc['name'], sc['path']))

    def add_shortcut(self):
        name = simpledialog.askstring("Nuevo Atajo", "Nombre del botón (ej: DISCORD):", parent=self.root)
        if not name:
            return
            
        path = filedialog.askopenfilename(title="Selecciona el ejecutable (.exe)", filetypes=[("Executables", "*.exe"), ("All Files", "*.*")])
        if not path:
            # Fallback to manual entry if they cancel file dialog
            path = simpledialog.askstring("Ruta del Atajo", "Introduce la ruta, URL o comando interno (ej: chrome):", parent=self.root)
            
        if name and path:
            self.shortcuts.append({"name": name.upper(), "path": path})
            self.refresh_tree()

    def remove_shortcut(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Selecciona un atajo de la lista para eliminarlo.")
            return
        
        item_values = self.tree.item(selected_item[0], 'values')
        # Remove from self.shortcuts
        self.shortcuts = [sc for sc in self.shortcuts if sc['name'] != item_values[0]]
        self.refresh_tree()

    def save_all(self):
        self.config["provider"] = self.provider_var.get()
        self.config["gemini_api_key"] = self.gemini_entry.get().strip()
        self.config["openai_api_key"] = self.openai_entry.get().strip()
        self.config["openclaw_url"] = self.openclaw_entry.get().strip()
        self.config["wake_word"] = self.wake_entry.get().strip().lower()
        self.config["location"] = self.loc_entry.get().strip()
        self.config["theme"] = self.theme_var.get()
        self.config["shortcuts"] = self.shortcuts
        
        save_config(self.config)
        
        # Notificar al backend de los cambios
        async def notify():
            try:
                async with websockets.connect("ws://127.0.0.1:8765") as ws:
                    await ws.send(json.dumps({"type": "action", "action": "update_theme", "theme": self.config["theme"]}))
                    await ws.send(json.dumps({"type": "action", "action": "update_shortcuts", "shortcuts": self.config["shortcuts"]}))
                    await asyncio.sleep(0.1)
            except Exception as e:
                print("No se pudo notificar al backend:", e)
                
        asyncio.run(notify())
        
        messagebox.showinfo("Guardado", "Configuración y atajos guardados correctamente.\nLos cambios se han aplicado al instante.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisSettingsApp(root)
    root.mainloop()
