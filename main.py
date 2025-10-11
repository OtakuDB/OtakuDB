from Source.Core.Session.Manager import SessionsManager

Manager = SessionsManager()
Session = Manager.create_session()
Manager.run_interface(Session)