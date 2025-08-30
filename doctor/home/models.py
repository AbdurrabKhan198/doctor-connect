from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class ContactInquiry(models.Model):
    """Model for storing contact form submissions"""
    
    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Phone Number",
        validators=[
            RegexValidator(
                regex=r'^[\+]?[1-9][\d]{0,15}$',
                message='Please enter a valid phone number'
            )
        ]
    )
    
    # Practice Information
    practice_name = models.CharField(max_length=200, verbose_name="Practice Name")
    specialty = models.CharField(
        max_length=100,
        choices=[
            ('family-medicine', 'Family Medicine'),
            ('cardiology', 'Cardiology'),
            ('dermatology', 'Dermatology'),
            ('orthopedics', 'Orthopedics'),
            ('pediatrics', 'Pediatrics'),
            ('dental', 'Dental'),
            ('ophthalmology', 'Ophthalmology'),
            ('neurology', 'Neurology'),
            ('psychiatry', 'Psychiatry'),
            ('surgery', 'Surgery'),
            ('other', 'Other'),
        ],
        verbose_name="Medical Specialty"
    )
    location = models.CharField(max_length=200, verbose_name="Practice Location")
    current_website = models.URLField(blank=True, verbose_name="Current Website")
    
    # Services Needed
    services_needed = models.JSONField(
        default=list,
        verbose_name="Services Interested In",
        help_text="List of services the doctor is interested in"
    )
    
    # Project Details
    budget_range = models.CharField(
        max_length=50,
        choices=[
            ('under-500', 'Under $500'),
            ('500-1000', '$500 - $1,000'),
            ('1000-2000', '$1,000 - $2,000'),
            ('2000-5000', '$2,000 - $5,000'),
            ('over-5000', 'Over $5,000'),
        ],
        blank=True,
        verbose_name="Monthly Budget Range"
    )
    
    timeline = models.CharField(
        max_length=50,
        choices=[
            ('immediately', 'Immediately'),
            ('1-month', 'Within 1 month'),
            ('3-months', 'Within 3 months'),
            ('6-months', 'Within 6 months'),
            ('planning', 'Just planning/exploring'),
        ],
        blank=True,
        verbose_name="Project Timeline"
    )
    
    # Message and Preferences
    message = models.TextField(verbose_name="Project Description")
    newsletter_subscription = models.BooleanField(
        default=False, 
        verbose_name="Newsletter Subscription"
    )
    
    # Metadata
    submitted_at = models.DateTimeField(default=timezone.now, verbose_name="Submission Date")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    # Status and Follow-up
    status = models.CharField(
        max_length=50,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('qualified', 'Qualified'),
            ('proposal', 'Proposal Sent'),
            ('negotiating', 'Negotiating'),
            ('closed', 'Closed'),
            ('lost', 'Lost'),
        ],
        default='new',
        verbose_name="Status"
    )
    
    priority = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium',
        verbose_name="Priority"
    )
    
    assigned_to = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Assigned To"
    )
    
    notes = models.TextField(blank=True, verbose_name="Internal Notes")
    last_contacted = models.DateTimeField(blank=True, null=True, verbose_name="Last Contacted")
    
    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['specialty', 'submitted_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.practice_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def days_since_submission(self):
        return (timezone.now() - self.submitted_at).days

class NewsletterSubscription(models.Model):
    """Model for newsletter subscriptions"""
    
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Last Name")
    subscribed_at = models.DateTimeField(default=timezone.now, verbose_name="Subscription Date")
    is_active = models.BooleanField(default=True, verbose_name="Active Subscription")
    source = models.CharField(
        max_length=100,
        choices=[
            ('contact-form', 'Contact Form'),
            ('website', 'Website Signup'),
            ('manual', 'Manual Entry'),
        ],
        default='website',
        verbose_name="Subscription Source"
    )
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email

class ContactMethod(models.Model):
    """Model for storing different contact methods"""
    
    name = models.CharField(max_length=100, verbose_name="Contact Method Name")
    type = models.CharField(
        max_length=50,
        choices=[
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('address', 'Address'),
            ('social', 'Social Media'),
            ('other', 'Other'),
        ],
        verbose_name="Contact Type"
    )
    
    value = models.CharField(max_length=500, verbose_name="Contact Value")
    description = models.TextField(blank=True, verbose_name="Description")
    is_primary = models.BooleanField(default=False, verbose_name="Primary Contact Method")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    
    class Meta:
        verbose_name = "Contact Method"
        verbose_name_plural = "Contact Methods"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.value}"

class FAQ(models.Model):
    """Model for frequently asked questions"""
    
    question = models.CharField(max_length=500, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")
    category = models.CharField(
        max_length=100,
        choices=[
            ('general', 'General'),
            ('pricing', 'Pricing'),
            ('services', 'Services'),
            ('technical', 'Technical'),
            ('support', 'Support'),
        ],
        default='general',
        verbose_name="Category"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['category', 'order', 'question']
    
    def __str__(self):
        return self.question

class Testimonial(models.Model):
    """Model for storing customer testimonials"""
    
    doctor_name = models.CharField(max_length=200, verbose_name="Doctor Name")
    practice_name = models.CharField(max_length=200, verbose_name="Practice Name")
    specialty = models.CharField(max_length=100, verbose_name="Medical Specialty")
    testimonial_text = models.TextField(verbose_name="Testimonial")
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Rating"
    )
    doctor_image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        verbose_name="Doctor Photo"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Featured Testimonial")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    
    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.doctor_name} - {self.practice_name}"

class Service(models.Model):
    """Model for storing service offerings"""
    
    name = models.CharField(max_length=200, verbose_name="Service Name")
    description = models.TextField(verbose_name="Service Description")
    short_description = models.CharField(max_length=300, verbose_name="Short Description")
    icon_class = models.CharField(max_length=100, verbose_name="Icon CSS Class")
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Base Price"
    )
    price_period = models.CharField(
        max_length=50,
        choices=[
            ('one-time', 'One Time'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        verbose_name="Price Period"
    )
    
    # Features
    features = models.JSONField(
        default=list,
        verbose_name="Service Features",
        help_text="List of features included in this service"
    )
    
    # Display
    is_featured = models.BooleanField(default=False, verbose_name="Featured Service")
    is_popular = models.BooleanField(default=False, verbose_name="Popular Service")
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class ContactLog(models.Model):
    """Model for logging all contact interactions"""
    
    inquiry = models.ForeignKey(
        ContactInquiry,
        on_delete=models.CASCADE,
        related_name='contact_logs',
        verbose_name="Contact Inquiry"
    )
    
    action = models.CharField(
        max_length=100,
        choices=[
            ('email_sent', 'Email Sent'),
            ('phone_call', 'Phone Call'),
            ('meeting_scheduled', 'Meeting Scheduled'),
            ('proposal_sent', 'Proposal Sent'),
            ('follow_up', 'Follow Up'),
            ('other', 'Other'),
        ],
        verbose_name="Action Taken"
    )
    
    description = models.TextField(verbose_name="Action Description")
    outcome = models.TextField(blank=True, verbose_name="Outcome")
    next_action = models.TextField(blank=True, verbose_name="Next Action")
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name="Scheduled Date")
    
    performed_by = models.CharField(max_length=100, verbose_name="Performed By")
    performed_at = models.DateTimeField(default=timezone.now, verbose_name="Performed At")
    
    class Meta:
        verbose_name = "Contact Log"
        verbose_name_plural = "Contact Logs"
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.inquiry.full_name} - {self.action} on {self.performed_at.strftime('%Y-%m-%d')}"
