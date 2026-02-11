try:
    from crewai_tools import FileReadTool, FileWriterTool
    print("Import successful: FileReadTool, FileWriterTool")
except ImportError as e:
    print(f"Import failed: {e}")
