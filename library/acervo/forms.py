from django import forms

from .models import BookReview


class BookReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} estrelas') for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = BookReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
