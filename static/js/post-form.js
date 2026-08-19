document.addEventListener('DOMContentLoaded', function () {

    // --- Panel SEO colapsable ---
    const seoToggle = document.getElementById('seo-panel-toggle');
    const seoBody = document.getElementById('seo-panel-body');
    const seoChevron = document.getElementById('seo-panel-chevron');
    seoToggle.addEventListener('click', function () {
        seoBody.classList.toggle('hidden');
        seoChevron.style.transform = seoBody.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    // --- Permalink editable ---
    const slugInput = document.getElementById('id_slug');
    const slugPreview = document.getElementById('slug-preview');
    const permalinkDisplay = document.getElementById('permalink-display');
    const permalinkEdit = document.getElementById('permalink-edit');
    let previousSlug = slugInput.value;

    document.getElementById('edit-permalink-btn').addEventListener('click', function () {
        previousSlug = slugInput.value;
        permalinkDisplay.classList.add('hidden');
        permalinkEdit.classList.remove('hidden');
        permalinkEdit.classList.add('flex');
        slugInput.focus();
    });
    document.getElementById('save-permalink-btn').addEventListener('click', function () {
        slugPreview.textContent = slugInput.value || 'se-generara-del-titulo';
        permalinkEdit.classList.add('hidden');
        permalinkEdit.classList.remove('flex');
        permalinkDisplay.classList.remove('hidden');
    });
    document.getElementById('cancel-permalink-btn').addEventListener('click', function () {
        slugInput.value = previousSlug;
        permalinkEdit.classList.add('hidden');
        permalinkEdit.classList.remove('flex');
        permalinkDisplay.classList.remove('hidden');
    });

    // --- Categoría estilo WordPress ---
    const categoryHidden = document.getElementById('id_category_name');

    function bindCategoryRadios() {
        document.querySelectorAll('.category-radio').forEach(function (radio) {
            radio.addEventListener('change', function () {
                categoryHidden.value = radio.value;
            });
        });
    }
    bindCategoryRadios();

    document.getElementById('add-category-toggle').addEventListener('click', function () {
        document.getElementById('add-category-box').classList.toggle('hidden');
    });

    document.getElementById('add-category-confirm').addEventListener('click', function () {
        const input = document.getElementById('new-category-input');
        const value = input.value.trim();
        if (!value) return;

        document.querySelectorAll('input[name="category_radio"]').forEach(function (r) {
            r.checked = false;
        });

        const label = document.createElement('label');
        label.className = 'flex items-center gap-2 text-sm text-gray-700';
        label.innerHTML = '<input type="radio" name="category_radio" value="' + value +
            '" class="h-4 w-4 text-brand-500 border-gray-300 focus:ring-brand-500 category-radio" checked> ' + value;
        document.getElementById('category-list').appendChild(label);
        bindCategoryRadios();

        categoryHidden.value = value;
        input.value = '';
        document.getElementById('add-category-box').classList.add('hidden');
    });
    // --- Imagen destacada estilo WordPress ---
const featuredInput = document.getElementById('id_featured_image');
const previewWrapper = document.getElementById('featured-image-preview-wrapper');
const previewImg = document.getElementById('featured-image-preview');
const dropzone = document.getElementById('featured-image-dropzone');
const featuredActions = document.getElementById('featured-image-actions');
const removeFeaturedBtn = document.getElementById('remove-featured-image');
const clearCheckbox = document.getElementById('id_featured_image-clear_id');

featuredInput.addEventListener('change', function () {
    if (featuredInput.files && featuredInput.files[0]) {
        previewImg.src = URL.createObjectURL(featuredInput.files[0]);
        previewWrapper.classList.remove('hidden');
        dropzone.classList.add('hidden');
        featuredActions.classList.remove('hidden');
        if (clearCheckbox) clearCheckbox.checked = false;
    }
});

if (removeFeaturedBtn) {
    removeFeaturedBtn.addEventListener('click', function () {
        previewWrapper.classList.add('hidden');
        featuredActions.classList.add('hidden');
        dropzone.classList.remove('hidden');
        featuredInput.value = '';
        if (clearCheckbox) clearCheckbox.checked = true;
    });
}
    // --- Etiquetas tipo chips ---
    const tagsHidden = document.getElementById('id_tags_input');
    const chipContainer = document.getElementById('tags-chip-container');
    const tagsTextInput = document.getElementById('tags-text-input');
    let currentTags = tagsHidden.value
        ? tagsHidden.value.split(',').map(function (t) { return t.trim(); }).filter(Boolean)
        : [];

    function renderChips() {
        chipContainer.innerHTML = '';
        currentTags.forEach(function (tag, index) {
            const chip = document.createElement('span');
            chip.className = 'inline-flex items-center gap-1 bg-brand-50 text-brand-700 text-xs font-medium px-2.5 py-1 rounded-full';
            chip.innerHTML = tag + ' <button type="button" data-index="' + index + '" class="remove-tag-btn hover:text-brand-900">&times;</button>';
            chipContainer.appendChild(chip);
        });
        tagsHidden.value = currentTags.join(', ');
        chipContainer.querySelectorAll('.remove-tag-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                currentTags.splice(parseInt(btn.dataset.index), 1);
                renderChips();
            });
        });
    }

    tagsTextInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const value = tagsTextInput.value.trim();
            if (value && currentTags.indexOf(value) === -1) {
                currentTags.push(value);
                renderChips();
            }
            tagsTextInput.value = '';
        }
    });

    renderChips();
});