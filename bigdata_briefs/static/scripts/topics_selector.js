// Topic Presets
const TOPIC_PRESETS = {
    finance: [
        "What key takeaways emerged from {company}'s latest earnings report?",
        "What notable changes in {company}'s financial performance metrics have been reported recently?",
        "Has {company} revised its financial or operational guidance for upcoming periods?",
        "What significant strategic initiatives or business pivots has {company} announced recently?",
        "What material acquisition, merger, or divestiture activities involve {company} currently?",
        "What executive leadership changes have been announced at {company} recently?",
        "What significant contract wins, losses, or renewals has {company} recently announced?",
        "What significant new product launches or pipeline developments has {company} announced?",
        "What material operational disruptions or capacity changes is {company} experiencing currently?",
        "How are supply chain conditions affecting {company}'s operations and outlook?",
        "What production milestones or efficiency improvements has {company} achieved recently?",
        "What cost-cutting measures or expense management initiatives has {company} recently disclosed?",
        "What notable market share shifts has {company} experienced recently?",
        "How is {company} responding to new competitive threats or significant competitor actions?",
        "What significant new product launches or pipeline developments has {company} announced?",
        "What specific regulatory developments are materially affecting {company}?",
        "How are current macroeconomic factors affecting {company}'s performance and outlook?",
        "What material litigation developments involve {company} currently?",
        "What industry-specific trends or disruptions are directly affecting {company}?",
        "What significant capital allocation decisions has {company} announced recently?",
        "What changes to dividends, buybacks, or other shareholder return programs has {company} announced?",
        "What debt issuance, refinancing, or covenant changes has {company} recently announced?",
        "Have there been any credit rating actions or outlook changes for {company} recently?",
        "What shifts in the prevailing narrative around {company} are emerging among influential investors?",
        "What significant events could impact {company}'s performance in the near term?",
        "What unexpected disclosures or unusual trading patterns has {company} experienced recently?",
        "Is there any activist investor involvement or significant shareholder actions affecting {company}?"
    ],
    all: [
        "What are the most important developments for {company}?"
    ],
    esg: [
        "What environmental initiatives or sustainability goals has {company} announced or achieved?",
        "What climate-related risks or opportunities is {company} facing?",
        "How is {company} managing its carbon footprint and environmental impact?",
        "What social responsibility initiatives or community engagement programs has {company} launched?",
        "What diversity, equity, and inclusion efforts has {company} implemented?",
        "What labor practices, employee relations, or workplace safety issues affect {company}?",
        "What governance changes, board composition updates, or executive compensation changes has {company} made?",
        "What ethical concerns, controversies, or compliance issues involve {company}?",
        "What ESG-related regulations or standards is {company} responding to?",
        "What stakeholder engagement or ESG reporting updates has {company} provided?"
    ],
    custom: []
};

// Handle topic preset changes
function handleTopicPresetChange() {
    const presetSelect = document.getElementById('topicPreset');
    const selectedPreset = presetSelect.value;
    
    if (selectedPreset === 'custom') {
        // Keep current topics
        return;
    }
    
    // Load preset topics
    if (TOPIC_PRESETS[selectedPreset]) {
        topic_sentences = [...TOPIC_PRESETS[selectedPreset]];
        renderSentences();
    }
}
window.handleTopicPresetChange = handleTopicPresetChange;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-form');
    const addButton = document.getElementById('add-button');
    const input = document.getElementById('new-sentence-input');
    const listContainer = document.getElementById('sentence-list');

    // --- FUNCTIONS ---

    // Function to render the list of topic_sentences
    const renderSentences = () => {
        // Clear the current list to avoid duplicates
        if (!listContainer) return;
        listContainer.innerHTML = '';

        // If there are no topic_sentences, display a message
        if (!topic_sentences || topic_sentences.length === 0) {
            listContainer.innerHTML = `<p class="text-zinc-500 text-center p-4 text-sm">No topics added yet. Add a topic above.</p>`;
            return;
        }

        // Create and append an element for each sentence in reverse order
        [...topic_sentences].reverse().forEach((sentence, reverseIndex) => {
            // Calculate the original index for deletion
            const originalIndex = topic_sentences.length - 1 - reverseIndex;
            
            // Create the main container for the list item
            const listItem = document.createElement('div');
            listItem.className = 'flex justify-between items-center bg-zinc-900/50 p-3 border border-zinc-700 rounded-lg text-sm';

            // Create the text element
            const sentenceText = document.createElement('span');
            sentenceText.textContent = sentence;
            sentenceText.className = 'text-zinc-300 flex-1 mr-3';

            // Create the delete button
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.type = 'button';
            deleteButton.className = 'bg-red-600/80 text-white font-medium px-3 py-1.5 rounded-md hover:bg-red-600 transition-colors text-xs';

            // Add an event listener to the delete button
            deleteButton.addEventListener('click', () => {
                deleteSentence(originalIndex);
            });

            // Append text and button to the list item
            listItem.appendChild(sentenceText);
            listItem.appendChild(deleteButton);

            // Append the list item to the main container
            listContainer.appendChild(listItem);
        });
    };

    // Function to add a new sentence
    const addSentence = () => {
        if (!input) return;
        const newSentence = input.value.trim(); // Get value and remove whitespace
        if (newSentence) { // Only add if the input is not empty
            // Validate that it contains {company}
            if (!newSentence.includes('{company}')) {
                alert('Topic must include {company} placeholder');
                return;
            }
            if (!topic_sentences) {
                topic_sentences = [];
            }
            topic_sentences.push(newSentence);
            input.value = ''; // Clear the input field
            renderSentences(); // Re-render the list
            
            // Switch to custom preset if not already
            const presetSelect = document.getElementById('topicPreset');
            if (presetSelect && presetSelect.value !== 'custom') {
                presetSelect.value = 'custom';
            }
        }
    };

    // Function to delete a sentence by its index
    const deleteSentence = (indexToDelete) => {
        // Filter out the sentence at the specified index
        topic_sentences = topic_sentences.filter((_, index) => index !== indexToDelete);
        renderSentences(); // Re-render the list
    };

    // Make renderSentences available globally
    window.renderSentences = renderSentences;

    // --- EVENT LISTENERS ---

    // Listen for form submission (e.g., pressing Enter)
    if (form) {
        form.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent page reload
            addSentence();
        });
    }

    // Listen for clicks on the add button
    if (addButton) {
        addButton.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            addSentence();
        });
    }

    // --- INITIAL RENDER ---
    // Render the initial list when the page loads
    if (listContainer) {
        renderSentences();
    }
});

// Make topic_sentences accessible globally
if (typeof topic_sentences === 'undefined') {
    window.topic_sentences = [];
}
