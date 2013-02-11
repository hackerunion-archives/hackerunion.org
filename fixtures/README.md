If the fixtures are broken (due to a "X matching query does not exist" or another issue related to calling cast() in a model), the content type numbers are off.

You'll need to modify the fixtures file to account for the new content type added. Search for "actual_type" and cross reference the value here with the values shown in the django_content_types table.

Thieeeeenksssssz!
