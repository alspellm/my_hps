import os

# Function to extract a key for sorting
def sorting_key(filename):
    parts = filename.split('_')
    if parts[1] == "initial":
        return (0, filename)
    elif parts[1].isdigit():
        return (int(parts[1]), filename)
    else:
        return (1, filename)  # For non-integer keys, keep them in their original order

# Define the base directory
external_png_dir = '/sdf/group/hps/users/alspellm/projects/THESIS/ana/zbi_html/zalpha_plots_html_test/1d_plots'
base_dir = 'zalpha_0pt3'
name = 'zalpha_0pt3'
os.makedirs(base_dir, exist_ok=True)

# Create file1.html
with open(os.path.join(base_dir, '%s.html'%(name)), 'w') as f:
    f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} Page</title>
</head>
<body>
    <h1>Welcome to the {name} Page</h1>
    <p>Click on the links below to explore variables and iterations:</p>
    
    <ul>
        <li><a href="variables/variables.html">variables</a></li>
        <li><a href="iterations/iterations.html">iterations</a></li>
    </ul>
</body>
</html>
    ''')


# List of subdirectories
list_of_vars = ['unc_vtx_cxx','unc_vtx_cyy','unc_vtx_czz']

# Create variables.html
variables_dir = os.path.join(base_dir, 'variables')
os.makedirs(variables_dir, exist_ok=True)
with open(os.path.join(variables_dir, 'variables.html'), 'w') as f:
    subdirectory_links = "\n".join([f'<li><a href="{subdir}/{subdir}.html">{subdir}</a></li>' for subdir in list_of_vars])
    f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Variables</title>
</head>
<body>
    <h1>Variables for {name}</h1>
    <!-- Content specific to variables -->
    <ul>
        {subdirectory_links}
    </ul>
</body>
</html>
    ''')


#Make subdirs
for subdir in list_of_vars:
    subdir_path = os.path.join(variables_dir, subdir)
    os.makedirs(subdir_path, exist_ok=True)

    # Create HTML page for each subdirectory
    with open(os.path.join(subdir_path, f'{subdir}.html'), 'w') as f:
        f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subdir} Page</title>
</head>
<body>
    <h1>Welcome to the {subdir} Page</h1>
    <p>Click on the links below to explore:</p>
    
    <ul>
        <li><a href="1d-plots/1d-plots.html">1D Plots</a></li>
        <!-- Add more links as needed -->
    </ul>
</body>
</html>
        ''')

 # Create 1d-plots subdirectory
    plots1d_dir = os.path.join(subdir_path, '1d-plots')
    os.makedirs(plots1d_dir, exist_ok=True)

    # Create 1d-plots.html
    with open(os.path.join(plots1d_dir, '1d-plots.html'), 'w') as f:
        # List matching PNG files
        matching_pngs = [filename for filename in sorted(os.listdir(external_png_dir)) if subdir in filename]
        # Filter and sort filenames based on the iteration number
        #sorted_pngs = sorted(matching_pngs, key=lambda x: int(x.split('_')[1]))
        sorted_pngs = sorted(matching_pngs, key=sorting_key)
        #png_links = "\n".join([f'<li><a href="{external_png_dir}/{filename}" target="_blank">{filename}</a></li>' for filename in matching_pngs])
        # Generate img tags for the PNG files
        #img_tags = "\n".join([f'<img src="{external_png_dir}/{filename}" alt="{filename}" width="300">' for filename in matching_pngs])
        # Generate div containers with img tags for the sorted PNG files
        #img_divs = "\n".join([f'<div><img src="{external_png_dir}/{filename}" alt="{filename}" width="300"></div>' for filename in sorted_pngs])
        # Generate div containers with clickable img tags for the sorted PNG files
        img_divs = "\n".join([
            f'<div><a href="{external_png_dir}/{filename}" target="_blank"><img src="{external_png_dir}/{filename}" alt="{filename}" width="1000"></a></div>'
            for filename in sorted_pngs
        ])

        f.write(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1D Plots</title>
    <style>
        div {{
            margin-bottom: 20px; /* Add spacing between images */
        }}
    </style>
</head>
<body>
    <h1>1D Plots</h1>
    <ul>
        {img_divs}
    </ul>
</body>
</html>
        ''')
print("File structure and HTML pages have been created.")
