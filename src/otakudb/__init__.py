from dublib.functions.system import check_python_minimal_version

from .core.session import Session
from .interfaces.cli.shell import Interface

def main():
	check_python_minimal_version(3, 12)
	
	session: Session = Session()
	cli_interface: Interface = Interface(session)
	cli_interface.run()

if __name__ == "__main__":
	main()
