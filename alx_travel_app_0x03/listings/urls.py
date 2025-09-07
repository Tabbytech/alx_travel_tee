from rest_framework.routers import DefaultRouter
from .views import ListingViewsets, BookingViewsets

router = DefaultRouter()
router.register(r'listings', ListingViewsets, basename='listing')
router.register(r'bookings', BookingViewsets, basename='booking')

urlpatterns = router.urls
