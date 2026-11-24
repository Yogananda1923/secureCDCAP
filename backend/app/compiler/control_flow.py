from typing import List, Dict, Set
from app.schemas.compiler_schemas import (
    IRInstructionItem,
    BasicBlockItem,
    CFGEdgeItem,
    CFGResult
)

class CFGBuilder:
    """
    Constructs Control Flow Graphs (CFG) and partitions Three-Address Code
    instructions into maximal linear sequences (Basic Blocks).
    """

    @staticmethod
    def build(instructions: List[IRInstructionItem]) -> CFGResult:
        if not instructions:
            empty_block = BasicBlockItem(
                id="B0",
                label="Entry / Exit",
                instructions=[],
                predecessors=[],
                successors=[]
            )
            return CFGResult(
                entry_block="B0",
                exit_blocks=["B0"],
                blocks=[empty_block],
                edges=[]
            )

        # 1. Identify leaders:
        # - The first instruction
        # - Any instruction that is the target of a jump / branch (LABEL or FUNC_ENTRY)
        # - Any instruction immediately following a jump, branch, or return
        leader_indices: Set[int] = {0}
        label_to_index: Dict[str, int] = {}

        for idx, instr in enumerate(instructions):
            if instr.opcode in ("LABEL", "FUNC_ENTRY") and instr.result:
                label_to_index[instr.result] = idx
                leader_indices.add(idx)
            elif instr.opcode == "FUNC_ENTRY" and instr.arg1:
                label_to_index[instr.arg1] = idx
                leader_indices.add(idx)

            if instr.opcode in ("JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "RETURN", "FUNC_EXIT"):
                if idx + 1 < len(instructions):
                    leader_indices.add(idx + 1)

        # Also register target of jumps as leaders
        for instr in instructions:
            if instr.opcode in ("JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE") and instr.result in label_to_index:
                leader_indices.add(label_to_index[instr.result])

        sorted_leaders = sorted(list(leader_indices))

        # 2. Partition into Basic Blocks
        blocks: List[BasicBlockItem] = []
        block_map: Dict[str, BasicBlockItem] = {}
        index_to_block_id: Dict[int, str] = {}

        for i, start_idx in enumerate(sorted_leaders):
            end_idx = sorted_leaders[i + 1] if i + 1 < len(sorted_leaders) else len(instructions)
            block_id = f"B{i}"
            block_instrs = instructions[start_idx:end_idx]
            
            # Determine block label
            first_op = block_instrs[0].opcode if block_instrs else "EMPTY"
            label = f"Block {i}"
            if first_op == "FUNC_ENTRY":
                label = f"Func {block_instrs[0].arg1}"
            elif first_op == "LABEL":
                label = f"Label {block_instrs[0].result}"

            bb = BasicBlockItem(
                id=block_id,
                label=label,
                instructions=block_instrs,
                predecessors=[],
                successors=[]
            )
            blocks.append(bb)
            block_map[block_id] = bb
            for idx in range(start_idx, end_idx):
                index_to_block_id[idx] = block_id

        # 3. Add Edges between Basic Blocks
        edges: List[CFGEdgeItem] = []
        exit_blocks: Set[str] = set()

        for i, bb in enumerate(blocks):
            if not bb.instructions:
                continue

            last_instr = bb.instructions[-1]
            op = last_instr.opcode

            if op == "RETURN" or op == "FUNC_EXIT":
                exit_blocks.add(bb.id)
                continue

            if op == "JUMP":
                target_label = last_instr.result
                if target_label in label_to_index:
                    target_idx = label_to_index[target_label]
                    target_block_id = index_to_block_id.get(target_idx)
                    if target_block_id:
                        edges.append(CFGEdgeItem(from_block=bb.id, to_block=target_block_id, label="jump"))
                        bb.successors.append(target_block_id)
                        block_map[target_block_id].predecessors.append(bb.id)
            elif op in ("JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                # Branch target
                target_label = last_instr.result
                if target_label in label_to_index:
                    target_idx = label_to_index[target_label]
                    target_block_id = index_to_block_id.get(target_idx)
                    if target_block_id:
                        branch_lbl = "false" if op == "JUMP_IF_FALSE" else "true"
                        edges.append(CFGEdgeItem(from_block=bb.id, to_block=target_block_id, label=branch_lbl))
                        bb.successors.append(target_block_id)
                        block_map[target_block_id].predecessors.append(bb.id)
                # Fallthrough to next block
                if i + 1 < len(blocks):
                    next_block_id = blocks[i + 1].id
                    fall_lbl = "true" if op == "JUMP_IF_FALSE" else "false"
                    edges.append(CFGEdgeItem(from_block=bb.id, to_block=next_block_id, label=fall_lbl))
                    bb.successors.append(next_block_id)
                    block_map[next_block_id].predecessors.append(bb.id)
            else:
                # Normal fallthrough to sequential block
                if i + 1 < len(blocks):
                    next_block_id = blocks[i + 1].id
                    edges.append(CFGEdgeItem(from_block=bb.id, to_block=next_block_id, label="fallthrough"))
                    bb.successors.append(next_block_id)
                    block_map[next_block_id].predecessors.append(bb.id)
                else:
                    exit_blocks.add(bb.id)

        entry_block_id = blocks[0].id if blocks else "B0"
        if not exit_blocks and blocks:
            exit_blocks.add(blocks[-1].id)

        return CFGResult(
            entry_block=entry_block_id,
            exit_blocks=list(exit_blocks),
            blocks=blocks,
            edges=edges
        )

