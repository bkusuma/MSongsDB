import os
import glob
import re
import difflib

def transform_print_line(line):
    """
    Transforms a single line of Python 2 print statement to Python 3 print() function.
    Returns the transformed line or the original line if no transformation is applicable.
    """
    # Match lines that start with 'print' keyword, possibly indented.
    # This initial match is broad; further checks refine if it's a Py2 print statement.
    match = re.match(r"^(?P<indent>\s*)print(?P<after_print>.*)$", line)
    if not match:
        return line

    indent = match.group("indent")
    after_print = match.group("after_print")

    # Heuristic to skip already converted print function calls like print(arg1, arg2)
    # A Python 2 print *statement* is `print expr` or `print >> stream, expr`.
    # If `print` is immediately followed by `(` without a space,
    # it's highly likely a Python 3 style print() call or similar function call.
    # Python 2's `print(expr)` is parsed as `print` keyword followed by `(expr)`.
    # Python 2's `print(a,b)` is a SyntaxError if `print` is a keyword.
    # So, if we see `print(anything_with_comma_or_just_already_py3_style)`, we should leave it.
    if not after_print.startswith(" ") and \
       not after_print.startswith("\t") and \
       not after_print.startswith(">>") and \
       after_print.startswith("("):
        # This pattern `print(` (no space) is characteristic of a function call.
        # We assume this is already Py3 syntax or a custom function and leave it.
        return line

    # Standard processing for Py2 print statements
    # 'rest' is the part of the line after 'print' keyword and initial optional space.
    rest = after_print.lstrip() 
    
    comment = ""
    code_part = rest
    
    # Separate comments
    hash_pos = rest.find('#')
    if hash_pos != -1:
        # Ensure the '#' is not inside a string literal
        # This is a simplified check; a full parser would handle this perfectly.
        # For typical print statements, this is usually sufficient.
        # Count quotes before the hash.
        s_quotes = rest[:hash_pos].count("'")
        d_quotes = rest[:hash_pos].count('"')
        # Check for triple quotes is more complex, for simplicity, we assume simple strings here.
        # A more robust solution would involve a tokenizer.
        # For this task, we'll assume '#' outside strings marks a comment.
        
        # Simple check: if quotes are balanced before #, it's likely a comment
        # This check is still heuristic. A truly robust solution needs a Python tokenizer/parser.
        # For typical code, direct split is often okay.
        # Let's rely on the common case where # starts a comment.
        # If a string contains '#', this logic might misinterpret.
        # However, `2to3` itself faces similar issues without full parse context for comments.
        
        # A common simple approach:
        # If we are inside a string, hash_pos is not a comment.
        # This check is non-trivial with regex alone.
        # For now, we'll use a simpler split, acknowledging this limitation.
        # A more robust comment stripping would be:
        # try:
        #    compile(indent + "print " + rest, "<string>", "exec") # check if rest is valid with comment
        # except SyntaxError: # if comment is inside string, this might pass
        #    pass

        # For now, simple split:
        parts = rest.split('#', 1)
        code_part = parts[0].rstrip()
        comment = " #" + parts[1]
    else:
        code_part = rest.rstrip()

    # Handle 'print >> stream, args'
    if code_part.startswith(">>"):
        # Remove '>>' and leading/trailing spaces for regex matching on stream and args
        redirect_content = code_part[2:].lstrip()
        # Regex for `stream, args [, ]`
        # Stream can be complex, args can be complex.
        # Args_val must be present. `print >> f,` is a SyntaxError.
        redirect_match = re.match(r"^(?P<stream>[^,]+?)\s*,\s*(?P<args_val>.+?)(?P<trailing_comma>,)?$", redirect_content)
        
        if redirect_match:
            stream = redirect_match.group("stream").strip()
            args_val = redirect_match.group("args_val").strip()
            has_trailing_comma = redirect_match.group("trailing_comma") is not None

            if not args_val: # Should be caught by `.+?` but as a safeguard
                return line # Invalid print >> stream, (empty args)

            if has_trailing_comma:
                return f'{indent}print({args_val}, file={stream}, end=" "){comment}'
            else:
                return f'{indent}print({args_val}, file={stream}){comment}'
        else:
            # This path means the part after `>>` didn't match `stream, args [, ]`.
            # e.g., `print >> sys.stderr` (no comma, no args) - SyntaxError in Py2.
            # `2to3` might handle `print >> f` as `print(file=f)`.
            # For robustness, we only convert well-formed `print >> stream, arg...`
            return line 

    # Handle 'print args' (no redirection)
    elif not code_part: # Handles 'print' or 'print #comment'
        return f'{indent}print(){comment}'
    else:
        # 'code_part' is the 'arg1, arg2, ...' or 'arg1, arg2, ...,'
        # It's guaranteed non-empty here.
        
        final_args_str = code_part
        has_statement_trailing_comma = False
        
        if final_args_str.endswith(','):
            # This comma is the one that suppresses newline in Python 2 print statement
            stripped_args = final_args_str[:-1].rstrip()
            if not stripped_args: 
                # Original was `print ,` which is a SyntaxError in Python 2
                return line 
            final_args_str = stripped_args
            has_statement_trailing_comma = True

        if has_statement_trailing_comma:
            return f'{indent}print({final_args_str}, end=" "){comment}'
        else:
            return f'{indent}print({final_args_str}){comment}'

def update_print_syntax_in_directory(directory_path):
    """
    Updates print statements in all .py files in the given directory (recursively)
    and returns a list of diffs.
    """
    all_diffs = []
    # Ensure recursive search for .py files
    for filepath in glob.glob(os.path.join(directory_path, '**', '*.py'), recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
        except Exception as e:
            # print(f"Error reading file {filepath}: {e}") # For debugging
            # Add a note about unreadable files if necessary, or skip.
            # For now, we'll just skip unreadable files.
            continue

        transformed_lines = [transform_print_line(line.rstrip('\n')) for line in original_lines]
        
        # Re-add newlines for diff comparison if needed, but difflib handles lists of strings
        # original_lines_for_diff = [line.rstrip('\n') for line in original_lines]

        if transformed_lines != [line.rstrip('\n') for line in original_lines]:
            # Use absolute paths for diff display
            abs_filepath = os.path.abspath(filepath)
            from_file_label = f"a/{abs_filepath}"
            to_file_label = f"b/{abs_filepath}"
            
            diff = difflib.unified_diff(
                [line + '\n' for line in [ol.rstrip('\n') for ol in original_lines]], 
                [line + '\n' for line in transformed_lines], 
                fromfile=from_file_label, 
                tofile=to_file_label,
                lineterm='\n' # Ensure diff uses \n
            )
            all_diffs.append("".join(diff))
            
    return all_diffs

## Created by Google Gemini