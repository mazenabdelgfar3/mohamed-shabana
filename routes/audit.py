from flask import Blueprint, request
from services.audit_service import get_audit_logs
from utils.helpers import json_response, parse_int
from utils.decorators import login_required

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')


@audit_bp.route('/logs', methods=['GET'])
@login_required
def list_logs():
    table_name = request.args.get('TableName')
    record_id = request.args.get('RecordId')
    action = request.args.get('Action')
    limit = parse_int(request.args.get('limit', 100))
    logs = get_audit_logs(
        table_name=table_name,
        record_id=parse_int(record_id) if record_id else None,
        action=action,
        limit=limit,
    )
    return json_response(logs)
