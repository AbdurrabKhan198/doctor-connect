from django import forms
from django.core.validators import RegexValidator
from .models import (
    ContactInquiry, NewsletterSubscription, FAQ, Testimonial, 
    ContactMethod, Service
)

class ContactInquiryForm(forms.ModelForm):
    """Form for contact inquiries from doctors"""
    
    # Custom fields for better UX
    services_checkboxes = forms.MultipleChoiceField(
        choices=[
            ('website-design', 'Professional Website Design'),
            ('seo-optimization', 'SEO Optimization'),
            ('appointment-system', 'Appointment Booking System'),
            ('digital-marketing', 'Digital Marketing'),
            ('google-business', 'Google Business Profile'),
            ('social-media', 'Social Media Management'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Services You're Interested In"
    )
    
    # Custom validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters except +
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
            if len(cleaned_phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
            return cleaned_phone
        return phone
    
    def clean_services_needed(self):
        services = self.cleaned_data.get('services_checkboxes', [])
        if not services:
            raise forms.ValidationError("Please select at least one service you're interested in.")
        return services
    
    class Meta:
        model = ContactInquiry
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'practice_name', 'specialty', 'location', 'current_website',
            'budget_range', 'timeline', 'message', 'newsletter_subscription'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'autocomplete': 'family-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number (optional)',
                'autocomplete': 'tel'
            }),
            'practice_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your practice name',
                'autocomplete': 'organization'
            }),
            'specialty': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select your medical specialty'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State (e.g., New York, NY)',
                'autocomplete': 'address-level2'
            }),
            'current_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com (optional)',
                'autocomplete': 'url'
            }),
            'budget_range': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select your budget range'
            }),
            'timeline': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select your timeline'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us about your practice, current challenges, and what you hope to achieve online...',
                'style': 'resize: vertical;'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'first_name': 'First Name *',
            'last_name': 'Last Name *',
            'email': 'Email Address *',
            'phone': 'Phone Number',
            'practice_name': 'Practice Name *',
            'specialty': 'Medical Specialty *',
            'location': 'Practice Location (City, State) *',
            'current_website': 'Current Website',
            'budget_range': 'Monthly Budget Range',
            'timeline': 'When do you want to get started?',
            'message': 'Tell us about your practice and goals *',
            'newsletter_subscription': 'I\'d like to receive updates about healthcare digital marketing trends and tips'
        }
        help_texts = {
            'phone': 'We\'ll use this to follow up with you if needed.',
            'current_website': 'If you have an existing website, please share the URL.',
            'budget_range': 'This helps us provide the most suitable solutions for your needs.',
            'timeline': 'Understanding your timeline helps us plan accordingly.',
            'message': 'The more details you provide, the better we can serve you.'
        }

class NewsletterSubscriptionForm(forms.ModelForm):
    """Form for newsletter subscriptions"""
    
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name (optional)',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name (optional)',
                'autocomplete': 'family-name'
            })
        }
        labels = {
            'email': 'Email Address *',
            'first_name': 'First Name',
            'last_name': 'Last Name'
        }

class QuickContactForm(forms.Form):
    """Simple form for quick contact requests"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
            'autocomplete': 'name'
        }),
        label='Name *'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address',
            'autocomplete': 'email'
        }),
        label='Email *'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)',
            'autocomplete': 'tel'
        }),
        label='Phone'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'How can we help you?',
            'style': 'resize: vertical;'
        }),
        label='Message *'
    )
    
    contact_preference = forms.ChoiceField(
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone Call'),
            ('either', 'Either is fine')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Preferred Contact Method *',
        initial='email'
    )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters except +
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
            if len(cleaned_phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
            return cleaned_phone
        return phone

class ContactMethodForm(forms.ModelForm):
    """Form for managing contact methods"""
    
    class Meta:
        model = ContactInquiry
        fields = ['status', 'priority', 'assigned_to', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team member name'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add internal notes about this inquiry...'
            })
        }
        labels = {
            'status': 'Current Status',
            'priority': 'Priority Level',
            'assigned_to': 'Assigned To',
            'notes': 'Internal Notes'
        }

class FAQForm(forms.ModelForm):
    """Form for managing FAQs"""
    
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the question'
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter the answer'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class TestimonialForm(forms.ModelForm):
    """Form for managing testimonials"""
    
    class Meta:
        model = Testimonial
        fields = [
            'doctor_name', 'practice_name', 'specialty', 'testimonial_text',
            'rating', 'doctor_image', 'is_featured', 'is_active'
        ]
        widgets = {
            'doctor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter doctor\'s name'
            }),
            'practice_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter practice name'
            }),
            'specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medical specialty'
                }),
            'testimonial_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter the testimonial text'
            }),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'doctor_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
