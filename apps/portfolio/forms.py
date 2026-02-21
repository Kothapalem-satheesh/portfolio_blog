from django import forms

from .models import Education, Profile, Project, Skill


class ContactForm(forms.Form):
    name    = forms.CharField(max_length=120)
    email   = forms.EmailField()
    subject = forms.CharField(max_length=160)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields = [
            "full_name", "title", "intro", "about",
            "email", "phone", "location",
            "github_url", "linkedin_url", "twitter_url", "resume_url",
            "photo",
        ]
        widgets = {
            "intro": forms.Textarea(attrs={"rows": 3}),
            "about": forms.Textarea(attrs={"rows": 5}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model  = Project
        fields = ["title", "summary", "tech_stack", "demo_url", "source_url", "image", "featured", "order"]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model  = Skill
        fields = ["name", "category", "level", "order"]


class EducationForm(forms.ModelForm):
    class Meta:
        model  = Education
        fields = ["degree", "institution", "start_year", "end_year", "description", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
