# i-msa-misc
A catch-all repository for analysis undertaken at MSA.

Use this repository for one-off code or analysis. Please use a standalone repository for work that belongs to a dedicated workstream.

## Organization

We organize separate one-off projects into folders under `i-msa-msc`. Each folder should be governed by a well-defined and reproducible development environment. [Poetry](https://python-poetry.org/) is a helpful tool for package and dependency management when using python.

## Contributing

### Getting started

Clone the repository to your desired location:
```bash
git clone https://github.com/your-username/i-msa-misc.git
cd i-msa-misc
```

### Development Rules

1. **Always develop on a new branch. Never commit directly to `main`.** This keeps the main branch stable and allows for proper code review.

    Create a new branch for each project addition:
    ```bash
    git checkout -b descriptive-name
    ```

2. **Try to keep branches focused and short-lived**. Avoid sprawling branches that address unrelated issues or remain unmerged for extended periods. This makes code review easier and reduces merge conflicts.

3. **Write in-line documentation.** Add comments to clarify or provide commentary on segments of code. Functions should have always have docstrings. For simple functions these can just be one-liners.

4. **Write a README for each top-level folder**. We need to know what the purpose of the code in each folder.

5. **Commit changes with clear, descriptive messages**:
    ```bash
    git add .
    git commit -m "descriptive summary of changes"
    ```

### Submitting Changes

1. **Push your branch** to origin:
    ```bash
    git push origin your-branch-name
    ```
2. **Create a pull request** on GitHub from your branch to the branch you want to merge into. This is usually the branch you split from.
3. **Tag another contributor to review your PR**. Also write a clear title and description of your changes.
4. **At least one other contributor should review and approve** your pull request before it can be merged. Make requested changes in additional commits on the same branch.
5. **Generally use the "Squash and merge" option** to merge your PR. This will help us keep the git history easy to review. Occassionally we may want the full branch history on the main branch, in which case you can do a simple merge.
