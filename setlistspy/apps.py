from django.apps import AppConfig


class SetlistSpyConfig(AppConfig):
    name = 'setlistspy.app'
    verbose_name = 'SetlistSpy'

    def ready(self):
        import setlistspy.app.signals
        # In case this gets optimized out, you probably want this here
        # import setlistspy.app.signals
        super(SetlistSpyConfig, self).ready()
