from celery import Task

from credit_project.loans.models import CreditRequest, Borrower, Offer
from credit_project.taskapp.celery import app

import logging


logger = logging.getLogger(__name__)


class CreateOfferRequestsTask(Task):
    name = 'credit_project.loans.tasks.CreateOfferRequestsTask'

    def run(self, borrower_id, offer_id=None):
        borrower = self.get_borrower(borrower_id)
        offers = self.get_offers(borrower)
        self.create_credit_requests(borrower, offers)

    def get_borrower(self, borrower_id):
        try:
            borrower = Borrower.objects.get(id=borrower_id)
        except Borrower.DoesNotExist:
            logger.error('CreateOfferRequestsTask: Анкета {} не найдена.'.format(borrower_id))
        else:
            return borrower

    def get_offers(self, borrower, offer_id=None):
        """Если не указано предложение, значит создаем по заявке на кредит
        для всех подходящих предложений
        """
        offers = None
        if offer_id:
            try:
                offer = Offer.objects.get(id=offer_id)
            except Offer.DoesNotExist:
                logger.error('CreateOfferRequestsTask: Предложение {} не найдено.'.format(offer_id))
            else:
                offers = [offer, ]
        else:
            offers = Offer.objects.active()
            offers = offers.filter(min_score__lte=borrower.score, max_score__gte=borrower.score)
        return offers

    def create_credit_requests(self, borrower, offers):
        for offer in offers:
            CreditRequest.objects.create(borrower=borrower, offer=offer)

app.tasks.register(CreateOfferRequestsTask)

# from choithrams.celery_app import app
#
#
# logger = logging.getLogger('tasks')
# Product = get_model('catalogue', 'Product')
#
#
# @app.task(ignore_result=True)
# def call_command(name, *args, **options):
#     dj_call_command(name=name, *args, **options)
#
#
# @app.task()
# def update_products():
#     logger.info(u"Updating products prices")
#     now = datetime.datetime.now()
#     products = Product.objects.all()
#     for product in products:
#         product.update_offers(now=now)
#
#     try:
#         update_index.Command().handle()
#     except Exception as ex:
#         logger.error(ex)
#
#     logger.info(u"Updating product prices. Done")
