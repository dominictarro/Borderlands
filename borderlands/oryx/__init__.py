"""
An ETL system for Oryx visually-confirmed equipment losses in the
Russo-Ukrainian War.

Page Structure
--------------
The Oryx loss pages are organized as follows:

```html
<article>
    ...
    <div>
        <!-- info about the article -->
    </div>
    ...
    <div>
        <h3>
            <!-- asset category and its summary statistics -->
        </h3>
        <ul>
            <li>
                <!-- asset model and its supporting data -->
                <a>
                    <!-- confirmed equipment losses -->
                    <!-- these are just image/video URLs, there may be more than one loss
                    per <a> tag -->
                </a>
                <a>
                    <!-- confirmed equipment losses -->
                </a>
                ...
            </li>
            ...
        </ul>
        <!-- repeat the pattern of h3 tags followed by respective ul tags -->
        ...
    </div>
    ...
</article>
```

In line with this data structure, the parser is designed to generate
standardized records of each loss like so

```text
for asset category
    for asset model
        for confirmed loss <a> tag
            for confirmed loss
                yield case
```

"""
