from wa.models import Language, Book, Paragraph, UserHistory, Document

def uploadDigi(para_id):
	'''
	a digitized document is uploaded
	first update the percentatge complete
	then add a row to the table specifying who read it
	then change the status of this chunk
	'''
	book_id = Paragraph.objects.get(pk = para_id).book
	Book.objects.get(pk = book_id).percentageCompleteDigi = Book.objects.get(pk = book_id).percentageCompleteDigi + 1
	
	
	
