from PySide6 import QtWidgets
from ..views.SpecStore import SpecStore
from ..views.Tokens import TokensSection
from ..views.Endpoints import EndpointsSection
from ..views.Headers import KVRow
from ..views.Results import ResultsSection


class TabsComponent(QtWidgets.QTabWidget):
    """Tab widget containing Headers, Endpoints, Tokens/Roles, and Results sections."""
    
    def __init__(self, store: SpecStore, parent=None):
        super().__init__(parent)
        self.store = store
        
        # Initialize sections
        self.headers = KVRow(
            on_add=lambda k, v: self.store.set_header(k, v),
            on_remove_key=lambda k: self.store.remove_header(k),
            store=self.store
        )
        self.endpoints = EndpointsSection(self.store)
        self.tokens = TokensSection(self.store)
        self.results = ResultsSection()
        
        # Add tabs
        self.addTab(self.endpoints, "Endpoints")
        self.addTab(self.tokens, "Tokens / Roles")
        self.addTab(self.headers, "Headers")
        self.addTab(self.results, "Results")

    
    def get_headers(self) -> KVRow:
        """Get the headers section."""
        return self.headers
    
    def get_endpoints(self) -> EndpointsSection:
        """Get the endpoints section."""
        return self.endpoints
    
    def get_tokens(self) -> TokensSection:
        """Get the tokens section."""
        return self.tokens
    
    def get_results(self) -> ResultsSection:
        """Get the results section."""
        return self.results
