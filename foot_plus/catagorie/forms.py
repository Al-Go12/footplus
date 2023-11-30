from catagorie.models import *
from  django import forms
   


class AddProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [ 'product_name', 'category',  'description', 'price', 'image','brand']

class AddVariantForm(forms.ModelForm):
    color = forms.ChoiceField(choices=color_choice, widget=forms.Select(attrs={'class': 'form-control'}))
    size = forms.ChoiceField(choices=size_choice, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model=varients
        fields=['product','color','size','stock','price','image','is_active']    

class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'description', 'price', 'brand' ]        

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name').strip()

        if not category_name:
            raise forms.ValidationError("Category name cannot be empty or contain only spaces.")

        # Check uniqueness
        if Category.objects.filter(category_name__iexact=category_name).exists():
            raise forms.ValidationError("Category name must be unique.")

        return category_name

    def clean_description(self):
        description = self.cleaned_data.get('description').strip()

        # You can add additional validation for description if needed

        return description
            