"""
Handler: User Deleted
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import os
from datetime import datetime
from pathlib import Path
from handlers.base import EventHandler
from typing import Dict, Any

message_options = {
    1: "Nous supprimons votre compte à votre demande. Merci d'avoir été client de notre magasin. Si jamais vous voulez créer une nouvelle compte, n'hésitez pas à nous contacter.",
    2: "Nous supprimons votre compte à votre demande. Merci d'avoir été employé de notre magasin. Si jamais vous voulez rejoindre l'équipe de nouveau, n'hésitez pas à nous contacter.",
    3: "Nous supprimons votre compte à votre demande. Merci d'avoir été employé de notre magasin. Si jamais vous voulez rejoindre l'équipe de nouveau, n'hésitez pas à nous contacter."
}

class UserDeletedHandler(EventHandler):
    """Handles UserDeleted events"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        super().__init__()
    
    def get_event_type(self) -> str:
        """Return the event type this handler processes"""
        return "UserDeleted"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Create an HTML email based on user deletion data"""
        self.logger.debug(event_data)
        user_id = event_data.get('id')
        name = event_data.get('name')
        email = event_data.get('email')
        user_type_id = event_data.get('user_type_id')
        datetime = event_data.get('datetime')

        message = message_options.get(user_type_id)

        current_file = Path(__file__)
        project_root = current_file.parent.parent   
        with open(project_root / "templates" / "goodbye_client_template.html", 'r') as file:
            html_content = file.read()
            html_content = html_content.replace("{{user_id}}", str(user_id))
            html_content = html_content.replace("{{name}}", name)
            html_content = html_content.replace("{{email}}", email)
            html_content = html_content.replace("{{message}}", message)
            html_content = html_content.replace("{{deletion_date}}", datetime)
        
        filename = os.path.join(self.output_dir, f"goodbye_{user_id}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.debug(f"Courriel HTML généré à {name} (ID: {user_id}), {filename}")