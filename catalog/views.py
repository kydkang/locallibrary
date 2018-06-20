from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm


def index(request):
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,
                 'num_instances_available':num_instances_available,'num_authors':num_authors, 
                 'num_visits':num_visits}, 
    )

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author 

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.\
        filter(borrower=self.request.user).\
        filter(status__exact='o').order_by('due_back')

class AllBorrowedListView(PermissionRequiredMixin,generic.ListView):
    permission_required = 'catalog.can_mark_returned' 
    model = BookInstance
    template_name ='catalog/all_borrowed.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


@permission_required('catalog.can_mark_returned')  
def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed') )
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
    return render(request, 'catalog/book_renew_librarian.html', 
                  {'form': form, 'bookinst':book_inst})

class AuthorCreate(PermissionRequiredMixin,CreateView):
    permission_required = 'catalog.can_mark_returned' 
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = 'catalog.can_mark_returned' 
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    permission_required = 'catalog.can_mark_returned' 
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin,CreateView):
    permission_required = 'catalog.can_mark_returned' 
    model = Book 
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = 'catalog.can_mark_returned' 
    model = Book 
    fields = '__all__'

class BookDelete(PermissionRequiredMixin,DeleteView):
    permission_required = 'catalog.can_mark_returned' 
    model = Book
    success_url = reverse_lazy('books')

