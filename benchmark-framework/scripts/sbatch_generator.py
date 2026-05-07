def generate_sbatch(template_path, output_path, replacements):

    with open(template_path) as f:
        content = f.read()

    for key, value in replacements.items():
        content = content.replace(f"{{{key}}}", value)

    with open(output_path, "w") as f:
        f.write(content)
