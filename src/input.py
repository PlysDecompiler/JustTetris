

class Input(object):
    """
    This is a shim to increase the distance to implementation specifics.
    This class documents an expected interface which is meant to be used duck-typing style.
    Create a class which implements any of the functions below and let it be called
    by one input-implementation.
    """
    def __init__(self):     assert(False and "This class is only an example do not inherit from it, see doc for more.")
    def key_down(self, key):                pass
    def key_up(self, key):                  pass
    def mouse_down(self, button):           pass
    def mouse_up(self, button):             pass
    def wheel_spin(self, degrees):          pass
    def joy_not_implemented_yet(self):      pass
    
    
class QtInputGrabber(object):
    """
    This class is an input-implementation, it is meant to be used as a mixin.
    Mix it into a Qt-object from which all the input should be grabbed and flushed
    towards an object which supports the interface documented through Input
    This is an Qt-specific implementation of the Input interface.
    """
    def __init__(self, grab_keyboard=False, grab_mouse=False):  # TODO change or remove entirely
        if grab_keyboard:
            self.grabKeyboard()
        if grab_mouse:
            self.grabMouse()
        
    class Subscription(object):
        def __init__(self, publisher, subscriber):
            self.publisher  = publisher
            self.subscriber = subscriber
            
        def chancel(self):
            del self.publisher.subscribers[self.subscriber]
        
    def subscribe(self, subscriber):
        # returns a subscription which can be canceled if not forgotten
        if not hasattr(self, 'subscribers'):
            self.subscribers = []
            self.grabKeyboard()
             
        self.subscribers.append(subscriber)
        return self.Subscription(self, subscriber)
        
    def keyPressEvent(self, event):
        for sub in self.subscribers:
            try:
                sub.key_down(event)
            except AttributeError:
                continue

    def keyReleaseEvent(self, event):
        for sub in self.subscribers:
            try:
                sub.key_up(event)
            except AttributeError:
                continue
            
    def mousePressEvent(self, event):
        for sub in self.subscribers:
            try:
                sub.mouse_down(event)
            except AttributeError:
                continue
        
    def mouseReleaseEvent(self, event):
        for sub in self.subscribers:
            try:
                sub.mouse_up(event)
            except AttributeError:
                continue
