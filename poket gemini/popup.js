document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const pageUrlInput = document.getElementById('page-url');
    const pageTitleInput = document.getElementById('page-title');
    const pageTagsInput = document.getElementById('page-tags');
    const saveButton = document.getElementById('save-button');
    const savedItemsList = document.getElementById('saved-items-list');
    const searchInput = document.getElementById('search-input');
    const messageContainer = document.getElementById('message-container');
    const noItemsMessage = document.getElementById('no-items-message');
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeIconLight = document.getElementById('theme-icon-light');
    const themeIconDark = document.getElementById('theme-icon-dark');

    // --- Theme Toggle Functionality ---
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            themeIconLight.classList.remove('hidden');
            themeIconDark.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            themeIconLight.classList.add('hidden');
            themeIconDark.classList.remove('hidden');
        }
    };

    // Load saved theme or default to system preference
    chrome.storage.sync.get('theme', ({ theme }) => {
        if (theme) {
            applyTheme(theme);
        } else {
            // Check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(prefersDark ? 'dark' : 'light');
        }
    });

    themeToggleButton.addEventListener('click', () => {
        const isDarkMode = document.documentElement.classList.toggle('dark');
        const newTheme = isDarkMode ? 'dark' : 'light';
        applyTheme(newTheme);
        chrome.storage.sync.set({ theme: newTheme }); // Save preference
    });


    // --- Load current tab info ---
    const loadCurrentTabInfo = () => {
        // Send message to background script to get tab info
        chrome.runtime.sendMessage({ action: "getCurrentTabInfo" }, (response) => {
            if (response && response.success && response.data) {
                pageUrlInput.value = response.data.url;
                pageTitleInput.value = response.data.title;
            } else {
                console.error("Error getting tab info:", response ? response.error : "No response");
                displayMessage("Could not load current page details.", "error");
                // Disable form if URL/Title can't be fetched, or handle gracefully
                pageUrlInput.value = "Error loading URL";
                pageTitleInput.value = "Error loading Title";
                saveButton.disabled = true;
            }
        });
    };

    // --- Display Messages ---
    const displayMessage = (text, type = 'success', duration = 3000) => {
        messageContainer.innerHTML = ''; // Clear previous messages
        const messageDiv = document.createElement('div');
        messageDiv.textContent = text;
        messageDiv.className = `message message-${type} p-3 rounded-md shadow`;
        messageContainer.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, duration);
    };

    // --- Render Saved Items ---
    const renderSavedItems = (itemsToRender) => {
        savedItemsList.innerHTML = ''; // Clear existing items
        if (!itemsToRender || itemsToRender.length === 0) {
            noItemsMessage.classList.remove('hidden');
            return;
        }
        noItemsMessage.classList.add('hidden');

        itemsToRender.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'saved-item-card bg-white dark:bg-gray-700 p-4 rounded-lg shadow hover:shadow-md transition-shadow duration-150 ease-in-out';
            listItem.dataset.itemId = item.id;

            const titleElement = document.createElement('h3');
            titleElement.className = 'text-md font-semibold text-indigo-700 dark:text-indigo-400 mb-1';
            const linkElement = document.createElement('a');
            linkElement.href = item.url;
            linkElement.textContent = item.title || 'Untitled';
            linkElement.target = '_blank'; // Open in new tab
            linkElement.className = 'hover:underline';
            titleElement.appendChild(linkElement);

            const urlElement = document.createElement('p');
            urlElement.textContent = shortenUrl(item.url, 40);
            urlElement.className = 'text-xs text-gray-500 dark:text-gray-400 mb-2';

            const tagsContainer = document.createElement('div');
            tagsContainer.className = 'flex flex-wrap gap-1 mb-2';
            if (item.tags && item.tags.length > 0) {
                item.tags.forEach(tag => {
                    const tagElement = document.createElement('span');
                    tagElement.textContent = tag;
                    tagElement.className = 'tag bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 px-2 py-1 text-xs rounded-full';
                    tagsContainer.appendChild(tagElement);
                });
            } else {
                const noTagElement = document.createElement('span');
                noTagElement.textContent = 'No tags';
                noTagElement.className = 'text-xs text-gray-400 dark:text-gray-500 italic';
                tagsContainer.appendChild(noTagElement);
            }
            
            const dateElement = document.createElement('p');
            dateElement.textContent = `Added: ${new Date(item.dateAdded).toLocaleDateString()}`;
            dateElement.className = 'text-xs text-gray-400 dark:text-gray-500 mb-2';


            const deleteButton = document.createElement('button');
            deleteButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            `;
            deleteButton.className = 'text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-500 p-1 rounded-md focus:outline-none focus:ring-2 focus:ring-red-400';
            deleteButton.title = "Delete Item";
            deleteButton.addEventListener('click', () => handleDeleteItem(item.id));
            
            const itemControls = document.createElement('div');
            itemControls.className = 'flex justify-between items-center mt-2';
            itemControls.appendChild(dateElement);
            itemControls.appendChild(deleteButton);


            listItem.appendChild(titleElement);
            listItem.appendChild(urlElement);
            listItem.appendChild(tagsContainer);
            listItem.appendChild(itemControls);
            // listItem.appendChild(deleteButton); // Moved to itemControls

            savedItemsList.appendChild(listItem);
        });
    };

    const shortenUrl = (url, maxLength) => {
        if (url.length <= maxLength) return url;
        try {
            const parsedUrl = new URL(url);
            let shortUrl = parsedUrl.hostname + (parsedUrl.pathname.length > 1 ? '/...' : '');
            if (shortUrl.length > maxLength) {
                shortUrl = parsedUrl.hostname.substring(0, maxLength - 3) + '...';
            }
            return shortUrl;
        } catch (e) { // Invalid URL
            return url.substring(0, maxLength - 3) + '...';
        }
    };

    // --- Load and Display Saved Items ---
    let allItems = []; // Cache for all items to enable client-side search
    const loadSavedItems = () => {
        chrome.runtime.sendMessage({ action: "getItems" }, (response) => {
            if (response && response.success) {
                allItems = response.data || [];
                filterAndRenderItems(); // Initial render with no search term
            } else {
                console.error("Error loading items:", response ? response.error : "No response");
                displayMessage("Could not load saved items.", "error");
                noItemsMessage.classList.remove('hidden');
            }
        });
    };

    // --- Filter and Render Items based on Search ---
    const filterAndRenderItems = () => {
        const searchTerm = searchInput.value.toLowerCase().trim();
        if (!searchTerm) {
            renderSavedItems(allItems);
            return;
        }
        const filteredItems = allItems.filter(item => {
            const titleMatch = item.title && item.title.toLowerCase().includes(searchTerm);
            const urlMatch = item.url && item.url.toLowerCase().includes(searchTerm);
            const tagMatch = item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm));
            return titleMatch || urlMatch || tagMatch;
        });
        renderSavedItems(filteredItems);
    };

    searchInput.addEventListener('input', filterAndRenderItems);

    // --- Handle Save Button Click ---
    saveButton.addEventListener('click', () => {
        const url = pageUrlInput.value.trim();
        const title = pageTitleInput.value.trim() || "Untitled Page"; // Default title if empty
        const tagsString = pageTagsInput.value.trim();
        const tags = tagsString ? tagsString.split(',').map(tag => tag.trim()).filter(tag => tag) : [];

        if (!url || !url.startsWith('http')) { // Basic URL validation
            displayMessage("Please provide a valid URL.", "error");
            return;
        }

        const newItem = {
            id: Date.now().toString(), // Simple unique ID
            url: url,
            title: title,
            tags: tags,
            dateAdded: new Date().toISOString()
        };

        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';

        chrome.runtime.sendMessage({ action: "savePage", data: newItem }, (response) => {
            saveButton.disabled = false;
            saveButton.textContent = 'Save Page';
            if (response && response.success) {
                displayMessage(`"${shortenText(title, 30)}" saved successfully!`, "success");
                pageTagsInput.value = ''; // Clear tags input
                loadSavedItems(); // Refresh list
            } else {
                displayMessage(response ? response.error : "Failed to save page.", "error");
            }
        });
    });

    // --- Handle Delete Item ---
    const handleDeleteItem = (itemId) => {
        // Optional: Add a confirmation dialog here if desired,
        // but custom modals are better than window.confirm for extensions.
        // For MVP, direct delete.
        chrome.runtime.sendMessage({ action: "deleteItem", itemId: itemId }, (response) => {
            if (response && response.success) {
                displayMessage("Item deleted successfully.", "success");
                loadSavedItems(); // Refresh list
            } else {
                displayMessage(response ? response.error : "Failed to delete item.", "error");
            }
        });
    };

    function shortenText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength - 3) + "...";
    }


    // --- Initial Load ---
    loadCurrentTabInfo();
    loadSavedItems();
});


// This is a placeholder for icons.
// Create a directory named "icons" in your extension's root.
// Add icon16.png, icon48.png, and icon128.png to it.
// You can find placeholder icons online (e.g., search "placeholder icon png")
// or create simple ones. For example, a simple bookmark-like shape.

// Example: icons/icon48.png (pseudo-content, create an actual image file)
// A simple blue square or a stylized 'P' would work for an MVP.