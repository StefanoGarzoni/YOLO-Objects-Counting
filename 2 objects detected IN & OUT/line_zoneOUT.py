from typing import List, Tuple
from typing import Dict
import numpy as np
import supervision as sv

"""
class Vector:
    start: sv.Point
    end: sv.Point

    def is_in(self, point: sv.Point) -> bool:
        v1 = Vector(self.start, self.end)
        v2 = Vector(self.start, point)
        cross_product = (v1.end.x - v1.start.x) * (v2.end.y - v2.start.y) - (
            v1.end.y - v1.start.y
        ) * (v2.end.x - v2.start.x)
        return cross_product < 0
"""

class Vector:
    start: sv.Point
    end: sv.Point

    def __init__(self, start: sv.Point, end: sv.Point):
        self.start = start
        self.end = end

    def is_in(self, point: sv.Point) -> bool: #self, point: sv.Point=None
        if point is None:
            point = self.end

        v1 = Vector(self.start, self.end)
        v2 = Vector(self.start, point)
        cross_product = (v1.end.x - v1.start.x) * (v2.end.y - v2.start.y) - (
            v1.end.y - v1.start.y
        ) * (v2.end.x - v2.start.x)
        return cross_product < 0



class LineZoneNew:
    """
    This class is responsible for counting the number of objects that cross a
    predefined line.

    !!! warning

        LineZone utilizes the `tracker_id`. Read
        [here](https://supervision.roboflow.com/trackers/) to learn how to plug
        tracking into your inference pipeline.

    Attributes:
        in_count (int): The number of objects that have crossed the line from outside
            to inside.
        out_count (int): The number of objects that have crossed the line from inside
            to outside.
    """

    def __init__(self, start: sv.Point, end: sv.Point):
        """
        Args:
            start (Point): The starting point of the line.
            end (Point): The ending point of the line.
        """
        self.vector = Vector(start=start, end=end)
        self.tracker_state: Dict[str, bool] = {}
        self.in_count: int = 0
        self.out_count: int = 0

    def trigger(self, detections: sv.Detections) ->  Tuple[List[int], List[int]]:

        crossed_in = np.full(len(detections), -1, dtype=int)
        crossed_out = np.full(len(detections), -1, dtype=int)
        


        for i, (xyxy, confidence, class_id, tracker_id) in enumerate(detections):
            #xyxy, _, confidence, class_id, tracker_id = detection
            if tracker_id is None:
                continue

            x1, y1, x2, y2 = xyxy
            anchors = [
                sv.Point(x=x1, y=y1),
                sv.Point(x=x1, y=y2),
                sv.Point(x=x2, y=y1),
                sv.Point(x=x2, y=y2),
            ]
            triggers = [self.vector.is_in(point=anchor) for anchor in anchors]

            if len(set(triggers)) == 2:
                continue

            tracker_state = triggers[0]

            if tracker_id not in self.tracker_state:
                self.tracker_state[tracker_id] = tracker_state
                continue

            if self.tracker_state.get(tracker_id) == tracker_state:
                continue

            self.tracker_state[tracker_id] = tracker_state
            if tracker_state:
                if class_id == 1: #1 = Telaio
                    self.in_count += 1
                crossed_in[i] = class_id
            else:
                self.out_count += 1
                crossed_out[i]= class_id

        return crossed_in, crossed_out
