from unittest import TestCase

from assertpy import assert_that

from shared.common import Resource, ResourceDigest
from shared.diagram import VPCDiagramsNetDiagram
from shared.diagramsnet import MX_FILE

INFLATED_XML = "<xml />"
DEFLATED_XML = (
    "7Vbfb5swEP5reFwFNpTkMSZpN6mTKlXbHicXDFg1nGWcQvrXzwbT8CObWqkPfVgSKb7vO+7O5++QPZxU3a2isvwOGRMe8rPOw3sP"
    "IRRfR+bPIieH+LFDCsWzAQvOwAN/YQ70HXrkGWtmjhpAaC7nYAp1zVI9w6hS0M7dchDzrJIWbAU8pFSs0V880+WAblB8xr8yXpRj"
    "5uB6OzAVHZ3dTpqSZtBOIHzwcKIA9LCquoQJ272xL8NzN39hXwtTrNZveeCF4JO/l7jKDz/utzddgw/qi4vyTMXRbdgVq09jB+Co"
    "Ba9Z8tpg38Mkh1onIED1Pth8b2xWUiiacTbjwh1B292E23NlAnGoDV+Dsm0iORdi8oxp4z4iBm+0gic2YfL+Y5iMNiXLXDnPTGlu"
    "Du2OPjJxDw134R9Ba6gmDjvBC0tokAalzkpNVcwkIKWuhLEDt0MnxwCNtuuKTUkbObQj552tg5jzlZasusLOwhVtm/BKsQaOKmXf"
    "UlsPMeawmntRKc1GGa1+Ixt6fbLjMZldsG4CuZO+ZVAxrU7GZWS3TnVu7iLs7PYs4ngzQOVEvyNG3dgUr5HPyjILJ653CA39F9on"
    "EFoL6imDtPkYkWH8yUR2vRLZz/tkpTMJvNZ9anPyETE1J74XGSax1hWKFsDSjudAsLZsjDmwtOM5ECzDB4v8wbLACbCyZuH9RX5/"
    "UqD5YXJx7JbjVUPN5rJtS67Zg6Sp7WprJPYGKV9UbqHgKPuUlxTbs7+fZXppRlG42QThYqpdqf8eRMFybSOa+nld3PXWHl944ex2"
    "JCab5WvgI97QKJwNT4jWwxNt/PX0hOPV6B3jY8zzRaPnJvc1fPgD"
)


class TestDiagramsNetDiagram(TestCase):
    sut = VPCDiagramsNetDiagram()

    def test_deflate_encode(self):
        result = VPCDiagramsNetDiagram.deflate_encode(INFLATED_XML)
        assert_that(result).is_equal_to(DEFLATED_XML)

    def test_decode_inflate(self):
        result = VPCDiagramsNetDiagram.decode_inflate(DEFLATED_XML)
        assert_that(result).is_equal_to(INFLATED_XML)

    def test_file_generation(self):
        general_resources = [
            Resource(
                digest=ResourceDigest(id="123", type="type"),
                name="name",
                details="details",
            )
        ]
        grouped_resources = {"": general_resources}
        relations = []
        result = self.sut.build_diagram(grouped_resources, relations)
        assert_that(result).starts_with(MX_FILE[:200])
