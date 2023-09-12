from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect,  HttpResponse
from . import util
import random
import re
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def getentry(request, title):
    entry_content = util.get_entry(title)

    if entry_content is None:
        entries = util.list_entries()
        matching_entries = [entry for entry in entries if title.lower() == entry.lower()]
        if len(matching_entries) == 1:
            return redirect('getentry', title=matching_entries[0])
        else:
            return HttpResponseNotFound("Entry not found")

    # Convert Markdown content to HTML
    entry_html = markdown2.markdown(entry_content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": entry_html  # Use the converted HTML content
    })


def search_results(request):
    query = request.GET.get('q', '')
    entries = util.list_entries()

    matching_entries = [entry for entry in entries if query.lower() in entry.lower()]

    if len(matching_entries) == 1:
        # If there's only one matching entry, redirect to that entry's page
        return redirect('getentry', title=matching_entries[0])
    else:
        # If there are multiple matching entries or no matches, show search results
        return render(request, "encyclopedia/search_results.html", {
            "query": query,
            "matching_entries": matching_entries
        })

def create_entry(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # Validate title (no special characters or spaces)
        if not re.match(r'^\w+$', title):
            return HttpResponse("Invalid title. Please use only letters, numbers, or underscores.")

        # Check if an entry with the same title already exists
        if util.get_entry(title) is not None:
            return HttpResponse("An entry with this title already exists.")

        # Save the new entry
        util.save_entry(title, content)

        # Redirect to the new entry's page
        return redirect('getentry', title=title)

    return render(request, "encyclopedia/create_entry.html")

def edit_entry(request, title):
    entry_content = util.get_entry(title)

    if request.method == "POST":
        new_content = request.POST.get("content")
        util.save_entry(title, new_content)
        return redirect('getentry', title=title)

    return render(request, "encyclopedia/edit_entry.html", {
        "title": title,
        "content": entry_content
    })

def random_page(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return redirect('getentry', title=random_entry)
    else:
        # Handle the case when there are no entries to choose from
        return HttpResponse("No entries available.")
