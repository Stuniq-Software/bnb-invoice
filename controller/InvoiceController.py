from fastapi import APIRouter, Request, Response
from dtypes import APIResponse, HttpStatus
from repository import InvoiceRepository
from util import Database, RedisSession

router = APIRouter(prefix="/api/v1/invoice", tags=["invoice"])
invoice_service = InvoiceRepository(
    db_session=Database(),
    redis_session=RedisSession()
)


@router.post("/")
async def generate_invoice(request: Request, response: Response):
    data = await request.json()
    booking_id = data["booking_id"]
    payment_id = data["payment_id"]
    try:
        success, data = await invoice_service.generate_invoice(booking_id, payment_id)
        if not success:
            response.status_code = 500
            return APIResponse(
                status=HttpStatus.INTERNAL_SERVER_ERROR,
                message="Failed to generate invoice",
                data=data
            )
        
        return APIResponse(
            status=HttpStatus.CREATED,
            message="Invoice generated successfully",
            data=data
        )
    except Exception as e:
        response.status_code = 500
        return APIResponse(
            status=HttpStatus.INTERNAL_SERVER_ERROR,
            message=str(e),
            data=None
        )

@router.get("/{booking_id}")
async def get_invoice(booking_id: str, response: Response):
    data = invoice_service.get_invoice(booking_id)
    if not data:
        response.status_code = 404
        return APIResponse(
            status=HttpStatus.NOT_FOUND,
            message="Booking not Found",
            data=None
        ).to_dict()
    
    api_response = APIResponse(
        status=HttpStatus.OK,
        message="Invoice Found",
        data=data
    )
    return api_response.to_dict()