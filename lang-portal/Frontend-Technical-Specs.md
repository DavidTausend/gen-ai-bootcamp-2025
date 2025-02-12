# Frontend Technical Specs

## Pages

### Dashboard `/dashboard`

#### Purpose

The purpose of this page is to provide a summary of learning and act as the deafult page when a user visit the web-app

#### Components

- Last study session
    show last activity used
    show when last activity used
    summarizes wrong vs correct from last activity
    has a link to the group

- Study progress
    * total words study eg 3/124
        - across all study sessions show the total of words studied out of a possible words in our database
    * display a mastery progress eg. 0%

- Quick stats
    * success rate eg. 80%
    * total study sesseion eg. 4
    * total active groups eg. 3
    * study streak eg. 4 days

- Start studying button
    * goes to study activities page

#### Needed API points

- GET /api/dashboard/last_study_session
- GET /api/dashboard/study_progress
- GET /api/dashboard/quick_stats

### Study Activities Index`/study_activities`

#### Purpose

The purpose of this page is to show a collection of study activities with a thumbnail and its name, to eiter launch or view the study activity.

#### Components

- Study activity Card
    * show a thumbnail of the study activity
    * the name of the study activity
    * a lau  button to take us to the launc page
    * the view pata to view more information about past study
    * sessions for this study activity

#### Needed API points

- GET /api/study_activities


#### Study Activity Show `/study_activities/:id`

#### Purpose

The purpose of this page is to show the details of a study activity and its past study sessions.

#### Components
- Name of study activity
- Thumbnail of study activity
- Description of study activity
- Launch button
- Study activities Paginated List
    * id
    * activityname
    * group name
    * Start time
    * end time (inferred by the last word_review_item submitted)
    * number of review items

#### Needed API points
- GET /api/study_activities/:id
- GET /api/study_activities/:id/sessions

#### Study Activity Launch `/study_activities/:id/launch`

#### Purpose
The purpose of this page is to launch a study activity.

#### Components
- Name of study activity
- Launch form
    * select field for group
    * launch now button

#### Behavior
After the form is submitted a new tab opens with the study activity based on its URL provided in the database.

Also the after form is submitted the page will redirect to the study session show page.

#### Needed API points
- POST /api/study_activities


### Words Index `/words`

#### Purpose
The purpose of this page is to show all words in our database.

#### Components
- Paginated Word List
    * Columns
        - German
        - English
        - Correct count
        - Wrong count
    * Pagination with 100 items per page
    * Clicking the German work will take us to the word show page

#### Needed API points
- GET /api/words

### Word Show `/words/:id`

#### Purpose
The purpose of this page is to show information about a specific word.

#### Components
- German
- English
- Study statistics
    * Correct count
    * Wrong count
- Word Groups
    * show an a seires of pills eg. tags
    * When group name is clicked it will take us to the group show page

#### Needed API points
- GET /api/words/:id

### Word Groups Index `/groups`

#### Purpose
The purpose of this page is to show a list of groups in our database.

#### Components
- Paginated Group List
    * Columns
        - Group Name
        - Word count
    * Clicking the group name will take us to the group show page

#### Needed API points
- GET /api/groups


### Group Show `/groups/:id`

#### Purpose
The purpose of this page is to show information about a specific group.

#### Components
- Group name
- Group Statistics
    * Total Word count
- Words in Group (Paginateds list of Words)
    * Should use the same component as the words index page
- Study Sessions (Paginated list of Study Sessions)
    * Should use the same component as the study activities index page

#### Needed API points
- GET /api/groups/:id (the name and groups stats)
- GET /api/groups/:id/words
- GET /api/groups/:id/study_sessions

### Study Sessions Index `/study_sessions`

#### Purpose
The purpose of this page is to show a list of study sessions in our database.

#### Components
- Paginated Study Session List
    * Columns
        - ID
        - Activity Name
        - Group Name
        - Start Time
        - End Time
        - Number of Review Items
    * Clicking the study session id will take us to the study session show page

#### Needed API points
- GET /api/study_sessions

### Study Session Show `/study_sessions/:id`

#### Purpose
The purpose of this page is to show information about a specific study session.

#### Components
- Study Session Details
    * Activity Name
    * Group Name
    * Start Time
    * End Time
    * Number of Review Items
- Words Review Items (Paginated list of Review Items)
    * Should use the same component as the words index page

#### Needed API points
- GET /api/study_sessions/:id
- GET /api/study_sessions/:id/words

### Setting page `/settings`

#### Purpose
The purpose of this page is to make configurations to the study portal.

#### Components
- Theme Selection eg. Light, Dark, System Default
- Reset History Button
    * this will delete all study sessions and word review items
- Full Reset Button
    * this will delete all study sessions and word review items

#### Needed API points
- POST /api/reset_history
- POST /api/full_reset