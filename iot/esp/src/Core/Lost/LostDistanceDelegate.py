from src.Framework.Distance.DistanceDelegate import DistanceDelegate

class LostDistanceDelegate(DistanceDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_measure(self, distance, name):
        if self.workshop and hasattr(self.workshop, "on_distance_event"):
             self.workshop.on_distance_event(distance, name)
