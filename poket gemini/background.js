// background.js
// Service worker for the OpenPocket extension

// --- Initialization ---
chrome.runtime.onInstalled.addListener(() => {
    console.log("OpenPocket MVP extension installed.");

    // Initialize storage if it doesn't exist
    chrome.storage.local.get(["savedItems"], (result) => {
        if (!result.savedItems) {
            chrome.storage.local.set({ savedItems: [] });
        }
    });

    // Create context menu item
    chrome.contextMenus.create({
        id: "savePageToOpenPocket",
        title: "Save to OpenPocket",
        contexts: ["page"]
    });
});

// --- Context Menu Handler ---
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "savePageToOpenPocket" && tab) {
        // Get page title and URL
        const pageUrl = tab.url;
        const pageTitle = tab.title || "Untitled Page";

        // For context menu, we don't have a direct way to ask for tags.
        // So, we save it without tags or with a default tag,
        // or potentially open the popup with pre-filled info (more complex).
        // For this MVP, let's save it with an empty tags array.
        const newItem = {
            id: Date.now().toString(), // Simple unique ID
            url: pageUrl,
            title: pageTitle,
            tags: [],
            dateAdded: new Date().toISOString()
        };

        saveItem(newItem)
            .then(() => {
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: "icons/icon48.png",
                    title: "Page Saved!",
                    message: `"${shortenText(pageTitle, 40)}" saved to OpenPocket.`,
                    priority: 0
                });
            })
            .catch(error => {
                console.error("Error saving from context menu:", error);
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: "icons/icon48.png",
                    title: "Save Failed",
                    message: `Could not save page. Error: ${error.message}`,
                    priority: 1
                });
            });
    }
});

// --- Helper Functions ---
function shortenText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substr(0, maxLength - 3) + "...";
}

// --- Core Storage Functions (Promisified) ---
function saveItem(item) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(["savedItems"], (result) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            const items = result.savedItems || [];
            // Check for duplicates based on URL
            if (items.some(existingItem => existingItem.url === item.url)) {
                return reject(new Error("This page is already saved."));
            }
            items.unshift(item); // Add to the beginning of the list
            chrome.storage.local.set({ savedItems: items }, () => {
                if (chrome.runtime.lastError) {
                    return reject(chrome.runtime.lastError);
                }
                resolve(item);
            });
        });
    });
}

function getItems() {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(["savedItems"], (result) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve(result.savedItems || []);
        });
    });
}

function deleteItem(itemId) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(["savedItems"], (result) => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            let items = result.savedItems || [];
            const initialLength = items.length;
            items = items.filter(item => item.id !== itemId);

            if (items.length === initialLength) {
                return reject(new Error("Item not found for deletion."));
            }

            chrome.storage.local.set({ savedItems: items }, () => {
                if (chrome.runtime.lastError) {
                    return reject(chrome.runtime.lastError);
                }
                resolve(itemId);
            });
        });
    });
}

// --- Message Handling from Popup ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "savePage") {
        saveItem(request.data)
            .then(savedItem => sendResponse({ success: true, data: savedItem }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Indicates asynchronous response
    } else if (request.action === "getItems") {
        getItems()
            .then(items => sendResponse({ success: true, data: items }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Indicates asynchronous response
    } else if (request.action === "deleteItem") {
        deleteItem(request.itemId)
            .then(itemId => sendResponse({ success: true, itemId: itemId }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Indicates asynchronous response
    } else if (request.action === "getCurrentTabInfo") {
        // This action is initiated by the popup to get current tab info
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs && tabs.length > 0) {
                const currentTab = tabs[0];
                sendResponse({
                    success: true,
                    data: {
                        url: currentTab.url,
                        title: currentTab.title || "Untitled Page"
                    }
                });
            } else {
                sendResponse({ success: false, error: "Could not get current tab information." });
            }
        });
        return true; // Indicates asynchronous response
    }
    // For other messages, or if not handled, return false or nothing.
});

console.log("OpenPocket background service worker started.");