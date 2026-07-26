import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Set
from .llama import estimate_tokens

@dataclass
class Remark:
    kind: str  # Passed, Missed, Analysis
    pass_name: str
    remark_name: str
    function: str
    file: Optional[str]
    line: Optional[int]
    column: Optional[int]
    message: str
    raw: str

    def fingerprint(self) -> str:
        # remark kind | pass | name | function | normalized message
        # We normalize message by stripping whitespace
        norm_msg = " ".join(self.message.split())
        return f"{self.kind}|{self.pass_name}|{self.remark_name}|{self.function}|{norm_msg}"

def parse_remarks(yaml_content: str) -> List[Remark]:
    remarks = []
    # LLVM YAML remarks are a sequence of documents separated by ---
    documents = yaml_content.split("---")
    for doc in documents:
        doc = doc.strip()
        if not doc:
            continue
        
        try:
            lines = doc.splitlines()
            if not lines:
                continue
                
            # First line usually looks like "!Passed", "!Missed", or "!Analysis"
            kind_match = re.match(r"^!(\w+)", lines[0])
            if not kind_match:
                continue
            kind = kind_match.group(1)
            
            data: Dict[str, Any] = {}
            args_list = []
            
            # We'll use a simple state machine to parse the document body
            # joining multi-line values if needed.
            body_lines = lines[1:]
            i = 0
            while i < len(body_lines):
                line = body_lines[i]
                stripped = line.strip()
                if not stripped:
                    i += 1
                    continue
                
                # Start of an argument in Args list
                if stripped.startswith("-"):
                    arg_match = re.match(r"^- (\w+):\s*(.*)", stripped)
                    if arg_match:
                        args_list.append({arg_match.group(1): arg_match.group(2).strip().strip("'\"")})
                    i += 1
                    continue
                
                kv_match = re.match(r"^(\w+):\s*(.*)", stripped)
                if kv_match:
                    key, value = kv_match.group(1), kv_match.group(2).strip()
                    
                    # Check for multi-line inline mapping
                    if value.startswith("{") and not value.endswith("}"):
                        full_value = value
                        i += 1
                        while i < len(body_lines) and not full_value.endswith("}"):
                            full_value += " " + body_lines[i].strip()
                            i += 1
                        value = full_value
                    else:
                        i += 1
                    
                    # Defensive check for mapping
                    if value.startswith("{") and value.endswith("}"):
                        inner = value[1:-1]
                        inner_data = {}
                        # Split by comma followed by a key
                        for item in re.split(r",\s*(?=\w+:|$)", inner):
                            if ":" in item:
                                ik, iv = item.split(":", 1)
                                inner_data[ik.strip()] = iv.strip().strip("'\"")
                        data[key] = inner_data
                    else:
                        data[key] = value.strip().strip("'\"")
                    continue
                
                i += 1 # Skip unexpected line
            
            # Extract fields defensivly
            pass_name = str(data.get("Pass", ""))
            remark_name = str(data.get("Name", ""))
            function = str(data.get("Function", ""))
            
            debug_loc = data.get("DebugLoc", {})
            file, line, column = None, None, None
            if isinstance(debug_loc, dict):
                file = debug_loc.get("File")
                line_val = debug_loc.get("Line")
                if line_val:
                    try: line = int(line_val)
                    except (ValueError, TypeError): line = None
                col_val = debug_loc.get("Column")
                if col_val:
                    try: column = int(col_val)
                    except (ValueError, TypeError): column = None
            
            # Message reconstructed from Args
            message_parts = []
            for arg in args_list:
                if isinstance(arg, dict):
                    for v in arg.values():
                        message_parts.append(str(v))
                elif isinstance(arg, str):
                    message_parts.append(arg)
            message = "".join(message_parts)
            
            remarks.append(Remark(
                kind=kind,
                pass_name=pass_name,
                remark_name=remark_name,
                function=function,
                file=file,
                line=line,
                column=column,
                message=message,
                raw=doc
            ))
        except Exception as e:
            # Skip this document if parsing fails fundamentally
            # This ensures one odd record doesn't stop the whole file
            # In a real environment, we might log this to stderr
            continue
        
    return remarks

def prioritize_remarks(remarks: List[Remark], target_source_name: str) -> List[Remark]:
    # Priority: Missed > Analysis > Passed
    kind_priority = {"Missed": 0, "Analysis": 1, "Passed": 2}
    
    # Also prioritize based on pass names and content as requested
    important_passes = {
        "loop-vectorize", "loop-unroll", "inline", "gvn", "licm", 
        "memdep", "slp-vectorizer", "regalloc", "tailcallelim"
    }
    
    def sort_key(r: Remark):
        kp = kind_priority.get(r.kind, 10)
        
        # Prioritize remarks referring to target source
        is_target_file = 0 if (r.file and target_source_name in r.file) else 1
        
        # Prioritize important optimization passes
        is_important_pass = 0 if any(p in r.pass_name.lower() for p in important_passes) else 1
        
        return (kp, is_target_file, is_important_pass)

    return sorted(remarks, key=sort_key)

def filter_remarks(remarks: List[Remark], already_seen_fingerprints: set) -> List[Remark]:
    # Filter out remarks already seen in previous iterations unless they changed
    # In practice, the fingerprint includes the message, so if message changes it's a new remark.
    return [r for r in remarks if r.fingerprint() not in already_seen_fingerprints]


def batch_remarks(
    remarks: List[Remark],
    max_tokens: int,
    tokenize_fn: Optional[callable] = None
) -> tuple[List[Remark], List[Remark]]:
    # Fit as many remarks as possible into max_tokens
    # Returns (selected_remarks, remaining_remarks)
    
    selected = []
    current_tokens = 0
    
    for i, r in enumerate(remarks):
        # We use the raw YAML text for token counting as it's what goes into the prompt
        remark_text = r.raw + "\n"
        
        tokens = tokenize_fn(remark_text) if tokenize_fn else estimate_tokens(remark_text)
        if tokens <= 0:
            tokens = estimate_tokens(remark_text)
            
        if current_tokens + tokens <= max_tokens:
            selected.append(r)
            current_tokens += tokens
        else:
            return selected, remarks[i:]
            
    return selected, []
