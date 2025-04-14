echo "Suppression des fichiers traqués qui sont maintenant ignorés..."

git ls-files --cached --ignored --exclude-from=.gitignore | while read file; do
    echo "Untracking: $file"
    git rm --cached "$file"
done

echo "Terminé ! Faut penser à faire un commit abeg haha..."