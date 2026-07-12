from __future__ import annotations

from pathlib import Path
import sys

import customtkinter as ctk
import tkinter as tk

from config import APP_NAME, APP_VERSION, PROJECTS_DIR
from core.app_logger import AppLogger
from core.job_queue import JobQueueManager
from ui.dashboard import DashboardPage
from ui.developer_console import DeveloperConsolePage
from ui.generator import GeneratorPage
from ui.new_project import NewProjectPage
from ui.projects import ProjectsPage
from ui.queue import QueuePage
from ui.settings import SettingsPage
from ui.speech import SpeechPage
from ui.theme import COLORS, body_font, title_font
from ui.workflow import WorkflowPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")



def resource_path(relative_path: str) -> Path:
    """Return a bundled resource path for normal and PyInstaller execution."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return bundle_root / relative_path


class ProjectApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(f"{APP_NAME} — {APP_VERSION}")
        self.geometry("1510x930")
        self.minsize(1220, 760)
        self.configure(fg_color=COLORS["window"])
        try:
            self.iconbitmap(str(resource_path("assets/AutoClip_Captioner.ico")))
        except (OSError, tk.TclError, NameError):
            pass

        self.current_page_name = ""
        self.previous_page_name = "Generator"
        self.logger = AppLogger()
        self.queue_manager = JobQueueManager(logger=self.logger)
        self.navigation_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_topbar()
        self.build_workspace()
        self.build_pages()

        self.bind("<F12>", self.toggle_developer_console)
        self.show_page("Generator")
        self.logger.info("Application interface ready", source="UI")

    def build_topbar(self) -> None:
        self.topbar = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0,
            fg_color=COLORS["topbar"],
        )
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_columnconfigure(1, weight=1)
        self.topbar.grid_propagate(False)

        brand = ctk.CTkFrame(self.topbar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=(20, 18), pady=10)

        ctk.CTkLabel(
            brand,
            text="▣",
            width=38,
            height=38,
            corner_radius=10,
            fg_color=COLORS["accent"],
            text_color="white",
            font=title_font(18),
        ).pack(side="left")

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            brand_text,
            text="AutoClip Captioner",
            anchor="w",
            font=body_font(18, "bold"),
        ).pack(side="left")
        ctk.CTkLabel(
            brand_text,
            text=APP_VERSION,
            text_color=COLORS["muted"],
            font=body_font(11),
        ).pack(side="left", padx=(10, 0), pady=(4, 0))

        navigation = ctk.CTkFrame(self.topbar, fg_color="transparent")
        navigation.grid(row=0, column=1)

        nav_items = [
            ("Dashboard", "⌂"),
            ("Generator", "⚡"),
            ("Projects", "□"),
        ]

        for name, icon in nav_items:
            button = ctk.CTkButton(
                navigation,
                text=f"{icon}  {name}",
                width=150,
                height=46,
                corner_radius=9,
                fg_color="transparent",
                hover_color=COLORS["panel_hover"],
                border_width=1,
                border_color=COLORS["border"],
                text_color=COLORS["text"],
                font=body_font(14, "bold"),
                command=lambda page=name: self.show_page(page),
            )
            button.pack(side="left", padx=6)
            self.navigation_buttons[name] = button

        utilities = ctk.CTkFrame(self.topbar, fg_color="transparent")
        utilities.grid(row=0, column=2, sticky="e", padx=(12, 20))

        self.queue_button = ctk.CTkButton(
            utilities,
            text="Queue",
            width=74,
            height=36,
            fg_color="transparent",
            hover_color=COLORS["panel_hover"],
            border_width=1,
            border_color=COLORS["border"],
            command=lambda: self.show_page("Queue"),
        )
        self.queue_button.pack(side="left", padx=4)

        self.console_button = ctk.CTkButton(
            utilities,
            text="F12",
            width=54,
            height=36,
            fg_color="transparent",
            hover_color=COLORS["panel_hover"],
            border_width=1,
            border_color=COLORS["border"],
            command=self.toggle_developer_console,
        )
        self.console_button.pack(side="left", padx=4)

        ctk.CTkButton(
            utilities,
            text="⚙",
            width=42,
            height=36,
            fg_color="transparent",
            hover_color=COLORS["panel_hover"],
            border_width=1,
            border_color=COLORS["border"],
            font=body_font(16, "bold"),
            command=lambda: self.show_page("Settings"),
        ).pack(side="left", padx=(4, 0))

    def build_workspace(self) -> None:
        self.content_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
        )
        self.content_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(14, 8),
        )
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        self.bottom_bar = ctk.CTkFrame(
            self,
            height=34,
            corner_radius=0,
            fg_color=COLORS["topbar"],
        )
        self.bottom_bar.grid(row=2, column=0, sticky="ew")
        self.bottom_bar.grid_columnconfigure(1, weight=1)
        self.bottom_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.bottom_bar,
            text="●  Ready",
            text_color=COLORS["success"],
            font=body_font(11),
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20)

        self.worker_label = ctk.CTkLabel(
            self.bottom_bar,
            text="Local worker ready",
            text_color=COLORS["muted"],
            font=body_font(10),
        )
        self.worker_label.grid(row=0, column=2, sticky="e", padx=20)

    def build_pages(self) -> None:
        self.generator_page = GeneratorPage(
            self.content_container,
            queue_manager=self.queue_manager,
            logger=self.logger,
            status_callback=self.set_status,
            projects_changed_callback=self.projects_changed,
            open_queue_callback=lambda: self.show_page("Queue"),
        )

        self.dashboard_page = DashboardPage(
            self.content_container,
            open_projects_callback=lambda: self.show_page("Projects"),
            new_project_callback=lambda: self.show_page("Generator"),
        )

        self.new_project_page = NewProjectPage(
            self.content_container,
            project_created_callback=self.projects_changed,
            status_callback=self.set_status,
        )

        self.projects_page = ProjectsPage(
            self.content_container,
            edit_project_callback=self.edit_project,
            status_callback=self.set_status,
            projects_changed_callback=self.projects_changed,
            new_project_callback=lambda: self.show_page("Generator"),
            workflow_callback=self.open_workflow,
        )

        self.settings_page = SettingsPage(self.content_container)

        self.workflow_page = WorkflowPage(
            self.content_container,
            status_callback=self.set_status,
            projects_changed_callback=self.projects_changed,
            queue_manager=self.queue_manager,
            open_queue_callback=lambda: self.show_page("Queue"),
        )

        self.developer_console_page = DeveloperConsolePage(
            self.content_container,
            logger=self.logger,
            close_callback=self.close_developer_console,
        )

        self.queue_page = QueuePage(
            self.content_container,
            queue_manager=self.queue_manager,
            status_callback=self.set_status,
        )

        self.speech_page = SpeechPage(
            self.content_container,
            status_callback=self.set_status,
        )

        self.pages = {
            "Dashboard": self.dashboard_page,
            "Generator": self.generator_page,
            "Projects": self.projects_page,
            "New Project": self.new_project_page,
            "Workflow": self.workflow_page,
            "Queue": self.queue_page,
            "Speech": self.speech_page,
            "Settings": self.settings_page,
            "Developer Console": self.developer_console_page,
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name: str) -> None:
        page = self.pages.get(page_name)
        if page is None:
            self.set_status(f"{page_name} page could not be found")
            return

        if page_name == "Dashboard":
            self.dashboard_page.refresh()
        elif page_name == "Projects":
            self.projects_page.refresh()
        elif page_name == "Workflow":
            self.workflow_page.refresh_projects()
        elif page_name == "Queue":
            self.queue_page.refresh_projects()
            self.queue_page.refresh()
        elif page_name == "Speech":
            self.speech_page.refresh_projects()

        page.tkraise()

        if page_name != "Developer Console":
            self.previous_page_name = page_name

        self.current_page_name = page_name

        for name, button in self.navigation_buttons.items():
            if name == page_name:
                button.configure(
                    fg_color=COLORS["accent_soft"],
                    border_color=COLORS["accent"],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    border_color=COLORS["border"],
                )

        if page_name == "Developer Console":
            self.developer_console_page.show_all()

        self.set_status(f"{page_name} selected")

    def toggle_developer_console(self, _event=None) -> None:
        if self.current_page_name == "Developer Console":
            self.close_developer_console()
        else:
            self.show_page("Developer Console")

    def close_developer_console(self) -> None:
        target = (
            self.previous_page_name
            if self.previous_page_name in self.pages
            else "Generator"
        )
        self.show_page(target)

    def set_status(self, message: str) -> None:
        self.status_label.configure(text=f"●  {message}")

    def projects_changed(self) -> None:
        self.dashboard_page.refresh()
        self.projects_page.refresh()
        self.workflow_page.refresh_projects()
        self.queue_page.refresh_projects()
        self.speech_page.refresh_projects()

    def edit_project(self, project_directory: Path) -> None:
        self.new_project_page.load_project(project_directory)
        self.show_page("New Project")

    def open_workflow(self, project_directory: Path) -> None:
        self.show_page("Workflow")
        self.workflow_page.project_choice.set(project_directory.name)

        for name, directory in self.workflow_page.project_lookup.items():
            if directory == project_directory:
                self.workflow_page.project_choice.set(name)
                break

        self.workflow_page.load_project(project_directory)


def close_application(application: ProjectApp) -> None:
    application.logger.info("Application closing", source="System")
    application.queue_manager.shutdown()
    application.destroy()


def main() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    application = ProjectApp()
    application.protocol(
        "WM_DELETE_WINDOW",
        lambda: close_application(application),
    )
    application.mainloop()


if __name__ == "__main__":
    main()
