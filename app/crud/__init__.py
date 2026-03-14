"""
CRUD Operations Package

Database operations for:
- user_crud: User management
- client_crud: Client management
- bot_crud: Bot management
- transaction_crud: Transaction/payment management
- spending_crud: Balance spending/deduction management
- deleted_bot_crud: Deleted bots archive management
"""
from app.crud.user_crud import (
    get_or_create_user,
    get_user_by_id,
    get_all_users,
    get_all_user_ids,
    get_users_grouped_by_admin
)
from app.crud.client_crud import (
    create_client,
    get_client_by_user_id,
    update_client,
    update_client_balance,
    get_all_clients,
    get_all_client_user_ids,
    update_client_language
)
from app.crud.bot_crud import (
    create_client_bot,
    get_client_bots,
    get_bot_by_id,
    update_bot_process_id,
    stop_client_bot,
    get_bot_by_token,
    update_bot_info,
    get_active_bot_by_owner,
    get_all_active_bots_grouped_by_owner,
    get_bots_to_start,
    get_bots_to_stop,
    update_bot_status,
    get_all_bots_for_monitoring,
    set_bot_stop_flag,
    update_bot_card_and_prices
)
from app.crud.transaction_crud import (
    create_transaction,
    update_transaction_status,
    get_user_transactions,
    get_pending_transactions,
    get_transaction_by_id
)
from app.crud.spending_crud import (
    create_spending,
    create_client_spending,
    create_user_spending,
    get_spendings_by_user,
    get_spendings_by_admin,
    get_all_spendings,
    get_total_spending_by_user,
    get_total_spending_by_admin,
    get_spending_stats,
    get_spendings_count
)
from app.crud.deleted_bot_crud import (
    get_bot_users_count,
    create_deleted_bot,
    delete_client_bot,
    get_deleted_bots_by_user,
    get_all_deleted_bots
)

__all__ = [
    "get_or_create_user",
    "get_user_by_id",
    "get_all_users",
    "get_all_user_ids",
    "get_users_grouped_by_admin",
    "create_client",
    "get_client_by_user_id",
    "update_client",
    "update_client_balance",
    "get_all_clients",
    "get_all_client_user_ids",
    "update_client_language",
    "create_client_bot",
    "get_client_bots",
    "get_bot_by_id",
    "update_bot_process_id",
    "stop_client_bot",
    "get_bot_by_token",
    "update_bot_info",
    "get_active_bot_by_owner",
    "get_all_active_bots_grouped_by_owner",
    "get_bots_to_start",
    "get_bots_to_stop",
    "update_bot_status",
    "get_all_bots_for_monitoring",
    "set_bot_stop_flag",
    "update_bot_card_and_prices",
    "create_transaction",
    "update_transaction_status",
    "get_user_transactions",
    "get_pending_transactions",
    "get_transaction_by_id",
    "create_spending",
    "create_client_spending",
    "create_user_spending",
    "get_spendings_by_user",
    "get_spendings_by_admin",
    "get_all_spendings",
    "get_total_spending_by_user",
    "get_total_spending_by_admin",
    "get_spending_stats",
    "get_spendings_count",
    "get_bot_users_count",
    "create_deleted_bot",
    "delete_client_bot",
    "get_deleted_bots_by_user",
    "get_all_deleted_bots",
]
