import pytest

def test_collected_item():
    collected_item = {
        "id": 1,
        "numista_id": 12345,
        "user_id": 67890,
        "type_id": 2,
        "issue_id": 3,
        "private_comment": "Private comment",
        "public_comment": "Public comment",
        "price": {
            "value": 100,
            "currency": "USD"
        },
        "collection": "My Collection",
        "pictures": ["image1.jpg", "image2.jpg"],
        "acquisition_place": "Local Shop",
        "serial_number": "SN123456",
        "internal_id": "INT123",
        "weight": 10.5,
        "size": "Medium",
        "axis": "Vertical",
        "grading_details": "Mint"
    }
    
    assert collected_item["id"] == 1
    assert collected_item["numista_id"] == 12345
    assert collected_item["user_id"] == 67890
    assert collected_item["type_id"] == 2
    assert collected_item["issue_id"] == 3
    assert collected_item["private_comment"] == "Private comment"
    assert collected_item["public_comment"] == "Public comment"
    assert collected_item["price"]["value"] == 100
    assert collected_item["price"]["currency"] == "USD"
    assert collected_item["collection"] == "My Collection"
    assert collected_item["pictures"] == ["image1.jpg", "image2.jpg"]
    assert collected_item["acquisition_place"] == "Local Shop"
    assert collected_item["serial_number"] == "SN123456"
    assert collected_item["internal_id"] == "INT123"
    assert collected_item["weight"] == 10.5
    assert collected_item["size"] == "Medium"
    assert collected_item["axis"] == "Vertical"
    assert collected_item["grading_details"] == "Mint"