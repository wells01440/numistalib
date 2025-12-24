"""
Quick CRUD demo using UserService directly (not a real test).
"""

from numistalib.config import Settings
from numistalib.services.users.service import UserService


def test_crud():
    """Demonstrate full CRUD workflow."""
    settings = Settings(
        api_key='e9HW50YiP7IuKt3B8c2Om5A3nYgnjL0Twg7UJAAb',
        client_id='526116',
        oauth_access_token='24614fdec126ccf247b7679efd09057ac367fabb'
    )

    client = Settings.to_client(settings)
    service = UserService(client)

    test_user_id = 423432

    print("\n" + "=" * 80)
    print("COLLECTION ITEM CRUD WITH UserService")
    print("=" * 80 + "\n")

    # 1. READ: Get all items
    print("1. READ: Get all collected items")
    print("-" * 80)
    items = service.get_collected_items(user_id=test_user_id)
    print(f"✓ Found {len(items)} items")
    
    if items:
        first = items[0]
        print(f"  First item ID: {first.id}")
        print(f"  Type ID: {first.type.id if first.type else 'N/A'}")
        print(f"  Quantity: {first.quantity}")
        print()

        # 2. READ: Get specific item
        print(f"2. READ: Get specific item {first.id}")
        print("-" * 80)
        item = service.get_collected_item(user_id=test_user_id, item_id=first.id)
        print(f"✓ Item ID: {item.id}")
        print(f"  Quantity: {item.quantity}")
        print(f"  Grade: {item.grade}")
        print()

        # 3. CREATE: Add new item
        print(f"3. CREATE: Add new item to collection")
        print("-" * 80)
        new_item = service.add_collected_item(
            user_id=test_user_id,
            type_id=420,  # Canadian 5 cents
            quantity=1,
            grade="vf"
        )
        print(f"✓ Created item ID: {new_item.id}")
        print(f"  Type: {new_item.type.title if new_item.type else 'N/A'}")
        print(f"  Quantity: {new_item.quantity}")
        print(f"  Grade: {new_item.grade}")
        print()

        # 4. UPDATE: Modify the item
        print(f"4. UPDATE: Modify item {new_item.id}")
        print("-" * 80)
        updated = service.edit_collected_item(
            user_id=test_user_id,
            item_id=new_item.id,
            quantity=3,
            grade="xf"
        )
        print(f"✓ Updated item ID: {updated.id}")
        print(f"  New quantity: {updated.quantity}")
        print(f"  New grade: {updated.grade}")
        print()

        # 5. DELETE: Remove the item
        print(f"5. DELETE: Remove item {new_item.id}")
        print("-" * 80)
        service.delete_collected_item(user_id=test_user_id, item_id=new_item.id)
        print(f"✓ Item deleted successfully")
        print()

        print("=" * 80)
        print("CRUD workflow complete!")
        print("=" * 80)
