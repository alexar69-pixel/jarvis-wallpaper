import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import load_config, save_config

class JarvisSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis Backend Settings")
        self.root.geometry("400x500")
        self.config = load_config()
        
        # Titulo
        ttk.Label(root, text="Configuración de Motores (Brain)", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Proveedor
        ttk.Label(root, text="Motor Activo:").pack(anchor="w", padx=20)
        self.provider_var = tk.StringVar(value=self.config.get("provider", "openclaw"))
        providers = [("OpenClaw (Local)", "openclaw"), ("Google Gemini", "gemini"), ("OpenAI (ChatGPT)", "openai")]
        for text, mode in providers:
            ttk.Radiobutton(root, text=text, variable=self.provider_var, value=mode).pack(anchor="w", padx=30)
            
        # Separador
        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        # API Keys
        ttk.Label(root, text="Gemini API Key:").pack(anchor="w", padx=20)
        self.gemini_entry = ttk.Entry(root, width=50)
        self.gemini_entry.insert(0, self.config.get("gemini_api_key", ""))
        self.gemini_entry.pack(padx=20, pady=5)
        
        ttk.Label(root, text="OpenAI API Key:").pack(anchor="w", padx=20)
        self.openai_entry = ttk.Entry(root, width=50)
        self.openai_entry.insert(0, self.config.get("openai_api_key", ""))
        self.openai_entry.pack(padx=20, pady=5)
        
        ttk.Label(root, text="OpenClaw Local URL:").pack(anchor="w", padx=20)
        self.openclaw_entry = ttk.Entry(root, width=50)
        self.openclaw_entry.insert(0, self.config.get("openclaw_url", "http://127.0.0.1:18789/v1/chat/completions"))
        self.openclaw_entry.pack(padx=20, pady=5)
        
        # Separador
        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        # Voz y Wake Word
        ttk.Label(root, text="Palabra de Activación (Wake Word):").pack(anchor="w", padx=20)
        self.wake_entry = ttk.Entry(root, width=20)
        self.wake_entry.insert(0, self.config.get("wake_word", "jarvis"))
        self.wake_entry.pack(anchor="w", padx=20, pady=5)

        ttk.Label(root, text="Ubicación (Clima):").pack(anchor="w", padx=20)
        self.loc_entry = ttk.Entry(root, width=30)
        self.loc_entry.insert(0, self.config.get("location", "Madrid"))
        self.loc_entry.pack(anchor="w", padx=20, pady=5)
        
        # Save Button
        ttk.Button(root, text="Guardar Configuración", command=self.save_all).pack(pady=20)

    def save_all(self):
        self.config["provider"] = self.provider_var.get()
        self.config["gemini_api_key"] = self.gemini_entry.get().strip()
        self.config["openai_api_key"] = self.openai_entry.get().strip()
        self.config["openclaw_url"] = self.openclaw_entry.get().strip()
        self.config["wake_word"] = self.wake_entry.get().strip().lower()
        self.config["location"] = self.loc_entry.get().strip()
        
        save_config(self.config)
        messagebox.showinfo("Guardado", "Configuración guardada correctamente.\nReinicia el backend si está ejecutándose.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisSettingsApp(root)
    root.mainloop()
