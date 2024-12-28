import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
from typing import Optional
from Segment import Segment
from Tag import *

class XmlSegmentSerializer:
    def __init__(self):
        self._segment_serializer = None

    def deserialize_segment(self, database_string: str) -> Optional[Segment]:
        """Deserializes the XML string into a Segment object."""
        segment = None
        try:
            root = ET.fromstring(database_string)
            # Deserialize the segment, assuming XML has relevant structure to map to a Segment
            segment = Segment._parse_segment(root)

            # Check if the segment is valid
            if not segment.is_valid():
                raise Exception("Invalid segment after deserialization")
        except Exception as e:
            print(f"Error during deserialization: {e}")
            raise
        return segment

    def serialize_segment(self, segment: Segment) -> str:
        """Serializes a Segment object into an XML string."""
        if segment is None:
            raise ValueError("segment cannot be None")
        if not segment.is_valid():
            raise Exception("Invalid segment")

        # Serialize the segment into XML
        segment_element = self._create_segment_element(segment)

        # Create a string representation of the XML
        return ET.tostring(segment_element, encoding='unicode', method='xml')



    def _create_segment_element(self, segment: Segment) -> ET.Element:
        """Creates an XML element from the Segment object."""
        segment_element = ET.Element("Segment")
        for key, value in segment.data.items():
            child = ET.SubElement(segment_element, key)
            child.text = saxutils.escape(value)  # Ensure text is properly escaped
        return segment_element