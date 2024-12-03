from __future__ import annotations
import os
import sys
from abc import ABC, abstractmethod
from .activator import Activator
if sys.version_info >= (3, 10):
    from importlib.resources import files
else:
    from importlib.resources import read_binary

class ViaTemplateActivator(Activator, ABC):
    @abstractmethod
    def templates(self):
        """
        Return a list of templates to use for generating activation scripts.
        
        :return: A list of template names
        """
        raise NotImplementedError

    def generate(self, creator):
        dest_folder = creator.bin_dir
        for template in self.templates():
            content = self.read_template(template)
            dest = os.path.join(dest_folder, template)
            with open(dest, 'wb') as file_handler:
                file_handler.write(content)

    def read_template(self, template):
        """
        Read the content of a template file.
        
        :param template: The name of the template file
        :return: The content of the template file
        """
        package = self.__class__.__module__
        if sys.version_info >= (3, 10):
            content = files(package).joinpath(template).read_bytes()
        else:
            content = read_binary(package, template)
        return self.instantiate_template(content, template, self.replacements(self.creator, self.dest_folder))

    @abstractmethod
    def replacements(self, creator, dest_folder):
        """
        Generate replacements for the template.
        
        :param creator: The creator object
        :param dest_folder: The destination folder
        :return: A dictionary of replacements
        """
        raise NotImplementedError

    def instantiate_template(self, content, template, replacements):
        """
        Replace placeholders in the template with actual values.
        
        :param content: The template content
        :param template: The template name
        :param replacements: A dictionary of replacements
        :return: The instantiated template content
        """
        for key, value in replacements.items():
            content = content.replace(key.encode(), value.encode())
        return content

__all__ = ['ViaTemplateActivator']
