from pydantic import RootModel


class ReportSourcesReverseMap(RootModel):
    root: dict[int, str]  # Maps ref_id to document_id and chunk mappings

    def keys(self):
        """Return the keys of the underlying dictionary."""
        return self.root.keys()

    def items(self):
        """Return the items of the underlying dictionary."""
        return self.root.items()

    def get(self, key):
        """Get a value from the underlying dictionary."""
        return self.root.get(key, None)
