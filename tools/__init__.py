"""
PyTools - A comprehensive collection of useful Python utilities
"""

__version__ = "1.0.0"
__author__ = "PyTools Team"

from .file_tools import *
from .text_tools import *
from .data_tools import *
from .web_tools import *
from .system_tools import *
from .crypto_tools import *
from .date_tools import *
from .math_tools import *
from .network_tools import *
from .string_tools import *
from .validation_tools import *
from .git_tools import *
from .agent_tools import *
from .user_tools import *

__all__ = [
    # File tools
    'read_file', 'write_file', 'append_file', 'copy_file', 'move_file',
    'delete_file', 'file_exists', 'get_file_size', 'get_file_extension',
    'list_files', 'list_directories', 'create_directory', 'delete_directory',
    'get_directory_size', 'find_files', 'backup_file', 'get_file_hash',
    'get_file_info',
    
    # Text tools
    'count_words', 'count_lines', 'count_characters', 'extract_emails',
    'extract_urls', 'extract_phone_numbers', 'remove_duplicates',
    'shuffle_text', 'reverse_text', 'capitalize_words', 'lowercase_words',
    'truncate_text', 'wrap_text', 'indent_text', 'remove_empty_lines',
    'normalize_whitespace', 'extract_hashtags', 'extract_mentions',
    'word_frequency', 'sentence_count', 'average_word_length',
    'remove_html_tags', 'strip_html',
    
    # Data tools
    'parse_csv', 'write_csv', 'parse_json', 'write_json', 'parse_xml',
    'flatten_dict', 'merge_dicts', 'filter_dict', 'sort_dict',
    'group_by', 'chunk_list', 'rotate_list', 'unique_list',
    'intersection', 'union', 'difference', 'zip_dicts', 'invert_dict',
    'deep_copy', 'dict_to_list', 'list_to_dict', 'safe_get', 'set_nested',
    
    # Web tools
    'is_valid_url', 'extract_domain', 'extract_path', 'parse_query_params',
    'build_url', 'is_url_safe', 'normalize_url', 'extract_urls_from_text',
    'url_encode', 'url_decode', 'get_url_components', 'is_same_domain',
    'make_absolute_url', 'sanitize_url',
    
    # System tools
    'get_system_info', 'get_disk_usage', 'get_memory_usage',
    'get_cpu_count', 'get_platform_info', 'get_environment_variables',
    'get_environment_variable', 'run_command', 'is_admin',
    'get_current_directory', 'change_directory', 'get_home_directory',
    'get_temp_directory', 'list_processes', 'get_username',
    
    # Crypto tools
    'hash_string', 'verify_hash', 'generate_random_string',
    'generate_uuid', 'generate_token', 'base64_encode', 'base64_decode',
    'base64_url_encode', 'base64_url_decode', 'hmac_hash',
    'generate_password', 'mask_string', 'constant_time_compare',
    'generate_api_key',
    
    # Date tools
    'get_current_date', 'get_current_time', 'get_current_datetime',
    'get_timestamp', 'format_date', 'parse_date', 'date_difference',
    'is_leap_year', 'get_days_in_month', 'add_days', 'subtract_days',
    'add_hours', 'add_minutes', 'get_weekday', 'get_weekday_number',
    'get_week_number', 'get_month_name', 'get_month_abbr',
    'start_of_day', 'end_of_day', 'start_of_month', 'end_of_month',
    'is_today', 'is_yesterday', 'is_tomorrow', 'days_until',
    'business_days_between', 'age_from_birthdate',
    
    # Math tools
    'calculate_percentage', 'calculate_average', 'calculate_median',
    'calculate_mode', 'calculate_std_dev', 'calculate_variance',
    'is_prime', 'get_factors', 'gcd', 'lcm', 'fibonacci', 'factorial',
    'permutations', 'combinations', 'power', 'sqrt', 'cbrt',
    'log', 'log10', 'log2', 'sin', 'cos', 'tan',
    'degrees_to_radians', 'radians_to_degrees', 'round_to',
    'floor', 'ceil', 'clamp', 'lerp', 'distance_2d', 'distance_3d',
    
    # Network tools
    'is_valid_ip', 'is_valid_ipv4', 'is_valid_ipv6', 'get_local_ip',
    'is_port_open', 'parse_mac_address', 'is_valid_mac_address',
    'get_hostname', 'get_host_by_name', 'get_ip_by_name',
    'ip_to_int', 'int_to_ip', 'get_subnet_mask', 'is_private_ip',
    'is_loopback_ip', 'get_network_address', 'get_broadcast_address',
    'count_ips_in_subnet', 'is_valid_port', 'get_common_ports',
    
    # String tools
    'slugify', 'camel_case', 'pascal_case', 'snake_case', 'kebab_case',
    'truncate', 'strip_html', 'remove_special_chars',
    'levenshtein_distance', 'is_palindrome', 'character_frequency',
    'remove_whitespace', 'pad_left', 'pad_right', 'pad_center',
    'remove_accents', 'is_uppercase', 'is_lowercase', 'is_title_case',
    'swap_case', 'repeat_string', 'insert_string', 'replace_all',
    'extract_between', 'count_substring', 'starts_with_any', 'ends_with_any',
    
    # Validation tools
    'is_email', 'is_phone', 'is_credit_card', 'is_strong_password',
    'is_valid_date', 'is_numeric', 'is_integer', 'is_alphanumeric',
    'is_empty', 'is_not_empty', 'is_url', 'is_ipv4', 'is_ipv6',
    'is_uuid', 'is_hex', 'is_base64', 'is_slug', 'is_username',
    'is_file_extension', 'is_in_range', 'is_positive', 'is_negative', 'is_zero',
    
    # Git tools
    'run_git_command', 'git_init', 'git_clone', 'git_add', 'git_add_all',
    'git_commit', 'git_push', 'git_pull', 'git_fetch', 'git_merge',
    'git_checkout', 'git_checkout_new_branch', 'git_create_branch',
    'git_delete_branch', 'git_list_branches', 'git_current_branch',
    'git_status', 'git_log', 'git_diff', 'git_show', 'git_stash',
    'git_stash_pop', 'git_stash_list', 'git_remote_list', 'git_remote_add',
    'git_remote_remove', 'git_tag_create', 'git_tag_list', 'git_tag_delete',
    'git_reset', 'git_revert', 'git_cherry_pick', 'git_blame',
    'git_config_get', 'git_config_set', 'git_is_repository', 'git_root',
    'git_ignore_add', 'git_clean',
    
    # Agent tools (Power Agent Tools)
    'agent_set_memory', 'agent_get_memory', 'agent_list_memory',
    'agent_clear_memory', 'agent_memory_history', 'agent_think',
    'agent_plan', 'agent_get_plan', 'agent_goal', 'agent_get_goal',
    'agent_context', 'agent_get_context', 'agent_clear_context',
    'agent_state', 'agent_get_state', 'agent_metadata', 'agent_get_metadata',
    'agent_task_start', 'agent_task_complete', 'agent_error',
    'agent_get_errors', 'agent_stats', 'agent_reset',
    
    # User tools (Power User Tools)
    'user_profile_create', 'user_profile_get', 'user_preferences_set',
    'user_preferences_get', 'user_bookmark_add', 'user_bookmarks_list',
    'user_notes_add', 'user_notes_list', 'user_history_add',
    'user_history_list', 'user_settings_get', 'user_settings_set',
    'user_quick_action', 'user_quick_actions_list', 'user_dashboard',
]
