import os
import subprocess
import sys
import threading
from tkinter import filedialog
from tkinter import messagebox
import warnings
import customtkinter as ctk
import imageio_ffmpeg
import librosa
import numpy as np
from PIL import Image


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


try:
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"


def get_musical_key(file_path):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y, sr = librosa.load(file_path, duration=60)
            chromogram = librosa.feature.chroma_stft(y=y, sr=sr)

            maj_profile = np.array(
                [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
            )
            min_profile = np.array(
                [6.33, 2.68, 3.52, 5.38, 2.6, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
            )

            maj_profile = maj_profile / np.linalg.norm(maj_profile)
            min_profile = min_profile / np.linalg.norm(min_profile)

            chroma_sum = np.sum(chromogram, axis=1)
            if np.linalg.norm(chroma_sum) == 0:
                return "Tono_Desconocido"
            chroma_sum = chroma_sum / np.linalg.norm(chroma_sum)

            best_corr = -1
            best_key = "Tono_Desconocido"
            keys = ["C", "CS", "D", "DS", "E", "F", "FS", "G", "GS", "A", "AS", "B"]

            for i in range(12):
                maj_rot = np.roll(maj_profile, i)
                min_rot = np.roll(min_profile, i)

                corr_maj = np.corrcoef(chroma_sum, maj_rot)[0, 1]
                corr_min = np.corrcoef(chroma_sum, min_rot)[0, 1]

                key_name = keys[i]

                if corr_maj > best_corr:
                    best_corr = corr_maj
                    best_key = f"{key_name}_Mayor"
                if corr_min > best_corr:
                    best_corr = corr_min
                    best_key = f"{key_name}_Menor"

            return best_key
    except Exception as e:
        print(f"Error detectando tonalidad {file_path}: {e}")
        return "Tono_Desconocido"


class AudioTransformerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Audio Transformer Pro - Cyber Edition")
        self.geometry("750x850")

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.selected_files = []
        self.is_converting = False

        logo_path = resource_path("heuristica.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                w_percent = 500 / float(logo_img.size[0])
                h_size = int(float(logo_img.size[1]) * float(w_percent))
                self.logo_ctk = ctk.CTkImage(
                    light_image=logo_img, dark_image=logo_img, size=(500, h_size)
                )
                self.logo_label = ctk.CTkLabel(self, text="", image=self.logo_ctk)
                self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 0))
            except Exception as e:
                print(f"Error cargando logo: {e}")

        self.title_label = ctk.CTkLabel(
            self,
            text="AUDIO TRANSFORMER PRO",
            font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
            text_color="#00FFCC",
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(10, 10))

        self.controls_frame = ctk.CTkFrame(
            self, border_width=2, border_color="#00FFCC", corner_radius=15
        )
        self.controls_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        tech_font = ctk.CTkFont(family="Consolas", size=13)
        self.select_btn = ctk.CTkButton(
            self.controls_frame,
            text="[1] Seleccionar Audios",
            command=self.select_files,
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            fg_color="#181818",
            border_width=1,
            border_color="#00FFCC",
            hover_color="#004d40",
        )
        self.select_btn.grid(row=0, column=0, padx=15, pady=15)

        self.format_label = ctk.CTkLabel(
            self.controls_frame,
            text="[2] Formato destino:",
            font=tech_font,
            text_color="#A9A9A9",
        )
        self.format_label.grid(row=0, column=1, padx=10, pady=15, sticky="e")

        self.target_format_var = ctk.StringVar(value="MP3")
        self.format_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            variable=self.target_format_var,
            values=["MP3", "WAV", "FLAC", "AAC", "OGG"],
            font=tech_font,
            fg_color="#181818",
            button_color="#00FFCC",
            button_hover_color="#00B38F",
        )
        self.format_menu.grid(row=0, column=2, padx=15, pady=15)

        self.enhance_var = ctk.BooleanVar(value=True)
        self.enhance_checkbox = ctk.CTkCheckBox(
            self.controls_frame,
            text="[3] Mejorar calidad (Filtro Neuronal - EBU R128)",
            variable=self.enhance_var,
            font=tech_font,
            text_color="#A9A9A9",
            hover_color="#00FFCC",
            border_color="#00FFCC",
        )
        self.enhance_checkbox.grid(
            row=1, column=0, columnspan=3, padx=15, pady=(0, 15), sticky="w"
        )

        self.files_textbox = ctk.CTkTextbox(
            self,
            state="disabled",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#00FF00",
            fg_color="#0C0C0C",
            border_width=1,
            border_color="#333333",
        )
        self.files_textbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.bottom_frame,
            text=">> Sistema en espera. Cargue archivos de audio...",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#A9A9A9",
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(
            self.bottom_frame, progress_color="#00FFCC"
        )
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.convert_btn = ctk.CTkButton(
            self.bottom_frame,
            text="[ INICIAR SECUENCIA ]",
            command=self.start_conversion,
            fg_color="#00FFCC",
            text_color="black",
            hover_color="#00B38F",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
        )
        self.convert_btn.grid(row=1, column=1, padx=10, pady=10)

    def select_files(self):
        filetypes = [
            ("Archivos de Audio", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.opus"),
            ("Todos los archivos", "*.*"),
        ]
        files = filedialog.askopenfilenames(
            title="Selecciona audios a transformar", filetypes=filetypes
        )
        if files:
            self.selected_files = list(files)
            self.update_files_list()
            self.status_label.configure(
                text=f"{len(self.selected_files)} archivos seleccionados."
            )

    def update_files_list(self):
        self.files_textbox.configure(state="normal")
        self.files_textbox.delete("0.0", "end")
        self.files_textbox.insert("end", "Archivos listos para procesar:\n")
        self.files_textbox.insert("end", "----------------------------------------\n")

        for file in self.selected_files:
            filename = os.path.basename(file)
            ext = os.path.splitext(filename)[1].upper()
            if not ext:
                ext = "DESCONOCIDO"
            self.files_textbox.insert("end", f"[Formato: {ext}] -> {filename}\n")

        self.files_textbox.configure(state="disabled")

    def toggle_ui_state(self, converting: bool):
        self.is_converting = converting
        state = "disabled" if converting else "normal"
        self.select_btn.configure(state=state)
        self.format_menu.configure(state=state)
        self.enhance_checkbox.configure(state=state)

        if converting:
            self.convert_btn.configure(state="disabled", text="Procesando...")
        else:
            self.convert_btn.configure(state="normal", text="Convertir y Mejorar")

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning(
                "Atencion", "Por favor selecciona al menos un archivo de audio."
            )
            return

        if self.is_converting:
            return

        self.toggle_ui_state(True)
        self.progress_bar.set(0)

        threading.Thread(target=self.conversion_worker, daemon=True).start()

    def conversion_worker(self):
        target_format = self.target_format_var.get().lower()
        enhance = self.enhance_var.get()
        total_files = len(self.selected_files)

        output_dir = os.path.join(
            os.path.dirname(self.selected_files[0]), "Audios_Transformados"
        )
        os.makedirs(output_dir, exist_ok=True)

        success_count = 0

        for i, input_file in enumerate(self.selected_files):
            filename = os.path.basename(input_file)
            base_name = os.path.splitext(filename)[0]

            self.status_label.configure(
                text=f"Analizando Tonalidad ({i + 1}/{total_files}): {filename}..."
            )

            key_name = get_musical_key(input_file)

            quality_tag = ""
            cmd = [FFMPEG_EXE, "-y", "-i", input_file]

            if enhance:
                cmd.extend(["-af", "loudnorm=I=-14:LRA=11:TP=-1.5"])

            if target_format == "mp3":
                quality_tag = "HQ_320kbps"
                cmd.extend(["-c:a", "libmp3lame", "-b:a", "320k"])
            elif target_format == "aac":
                quality_tag = "HQ_256kbps"
                cmd.extend(["-c:a", "aac", "-b:a", "256k"])
            elif target_format == "ogg":
                quality_tag = "HQ_Q8"
                cmd.extend(["-c:a", "libvorbis", "-q:a", "8"])
            elif target_format == "flac":
                quality_tag = "Lossless"
                cmd.extend(["-c:a", "flac"])
            elif target_format == "wav":
                quality_tag = "PCM_16bit"
                cmd.extend(["-c:a", "pcm_s16le"])

            enhance_tag = "_Mejorado" if enhance else ""
            quality_str = f"{quality_tag}{enhance_tag}"

            output_filename = (
                f"{base_name}_[{key_name}]_[{quality_str}].{target_format}"
            )
            output_path = os.path.join(output_dir, output_filename)

            self.status_label.configure(
                text=f"Convirtiendo ({i + 1}/{total_files}): {filename} -> {output_filename}..."
            )
            cmd.append(output_path)

            try:
                creationflags = (
                    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags,
                )
                success_count += 1
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

            progress = (i + 1) / total_files
            self.progress_bar.set(progress)

        self.status_label.configure(
            text=f"Completado. {success_count}/{total_files} archivos guardados en: {output_dir}"
        )
        self.toggle_ui_state(False)


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = AudioTransformerApp()
    app.mainloop()

