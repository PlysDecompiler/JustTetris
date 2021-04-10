#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def lazy_set_default(dictionary, key, closure):
    try:
        return dictionary[key]
    except KeyError:
        dictionary[key] = result = closure()
        return result    


class Entity(object):
    def __init__(self):
        pass
        # self.scene = None
    
    def purge(self):
        self.scene.purge(self)


class Scene(object):
    """
    A space of things which are.
    A collection of state.
    
    TODO
    reason about suiting interfaces, needed features.
    """
    def __init__(self):
        self.entity_types = dict()
    
    def add(self, entity, name=None):
        """
        If name is given the entity is added to the scene AND added to the
        dynamic_members which are accessible via attribute notation
        """
        if hasattr(entity, "scene"):
            raise ValueError("This object already belongs to a scene!")
        else:
            if not isinstance(entity, Entity):
                print("WARNING you added an object to the scene which isn't a subclass of Entity.")
                print("""You either have to implement a purge function yourself and call that
                or manually purge it from the scene.""")
            
            if name:
                setattr(entity, "name", name)
                setattr(self, name, entity)
            
            type_ = entity.__class__        # later add type specific search optimizations?
            instances = lazy_set_default(self.entity_types, type_, list)
            instances.append(entity)
            setattr(entity, "scene", self)

    def purge_silently(self, entity):
        try:
            self.purge(entity)
        except ValueError:
            pass

    def purge(self, entity):
        assert(self == entity.scene)
        try:
            if hasattr(entity, "name"):
                delattr(self, entity.name)
            
            type_ = entity.__class__
            instances = self.entity_types[type_]
            instances.remove(entity)
        
        except (KeyError, ValueError):
            raise ValueError("Your object is not in this scene so it can't be purged")

    def iter_instances(self, type_of_instances):
        try:
            instances = self.entity_types[type_of_instances]
            return iter(instances)
        except KeyError:
            # raise ValueError("This scene does not contain any instances of type '%s.%s'" % \
            # (type_of_instances.__module__, type_of_instances.__name__))
            return []  # TODO find a better way to return an empty iterable

    def for_all(self, type_of_instances, closure):
        try:
            instances = self.entity_types[type_of_instances]
            for e in instances:
                closure(e)
        except KeyError:
            # raise ValueError("This scene does not contain any instances of type '%s.%s'" % \
            # (type_of_instances.__module__, type_of_instances.__name__))
            pass

    def get_list(self, type_of_instances):
        # TODO look whether one can refactor away the need for this method
        try:
            instances = self.entity_types[type_of_instances]
            return instances
        except KeyError:
            raise ValueError("This scene does not contain any instances of type '%s.%s'" %
                             (type_of_instances.__module__, type_of_instances.__name__)
                             )
