"""
File Executor - Write artifacts to disk, generate patches, send communications

Handles Step 8 execution actions:
- Write code/infra/comms artifacts to local filesystem
- Generate git patches for code changes
- Send email and calendar invites
- Update JIRA tickets
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from database import get_protobot_session, get_ideabot_session, get_project
from config import settings

logger = logging.getLogger(__name__)


class FileExecutor:
    """
    File execution and artifact management.

    Responsibilities:
    - Write all generated artifacts to disk
    - Generate git patch files
    - Send communications (email/calendar)
    - Update JIRA tickets
    - Support mock and real modes
    """

    async def _setup_context_directory(self, project_id: str, output_path: Path):
        """
        Create context directory and copy reference materials from IdeaBot session.

        Creates:
        - context/
        - context/skills/
        - context/diagrams/
        - context/docs/
        - context/code-samples/
        - context/workflows/
        - context/README.md
        """
        import base64

        # Get IdeaBot session with reference materials
        ideabot_session = await get_ideabot_session(project_id)
        if not ideabot_session or not ideabot_session.get('reference_materials'):
            logger.info("No reference materials to copy")
            return

        try:
            references = json.loads(ideabot_session['reference_materials'])
        except:
            logger.warning("Failed to parse reference materials")
            return

        if not references:
            return

        # Create context directory structure
        context_dir = output_path / 'context'
        context_dir.mkdir(exist_ok=True)

        subdirs = {
            'skill': context_dir / 'skills',
            'code': context_dir / 'code-samples',
            'diagram': context_dir / 'diagrams',
            'document': context_dir / 'docs',
            'other': context_dir / 'workflows'
        }

        for subdir in subdirs.values():
            subdir.mkdir(exist_ok=True)

        # Copy reference materials to appropriate subdirectories
        readme_sections = {
            'skills': [],
            'diagrams': [],
            'documents': [],
            'code-samples': [],
            'workflows': []
        }

        for ref in references:
            category = ref.get('category', 'other')
            filename = ref.get('filename', 'unnamed.txt')
            content = ref.get('content', '')
            note = ref.get('note', '')

            # Determine target directory
            if category == 'skill':
                target_dir = subdirs['skill']
                readme_key = 'skills'
            elif category == 'code':
                target_dir = subdirs['code']
                readme_key = 'code-samples'
            elif category == 'diagram':
                target_dir = subdirs['diagram']
                readme_key = 'diagrams'
            elif category == 'document':
                target_dir = subdirs['document']
                readme_key = 'documents'
            else:
                target_dir = subdirs['other']
                readme_key = 'workflows'

            # Write file
            file_path = target_dir / filename

            try:
                # Handle base64 encoded content (images, PDFs)
                if content.startswith('data:'):
                    # Extract base64 data
                    _, data = content.split(',', 1)
                    decoded = base64.b64decode(data)
                    with open(file_path, 'wb') as f:
                        f.write(decoded)
                else:
                    # Plain text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                # Add to README section
                readme_sections[readme_key].append({
                    'filename': filename,
                    'note': note
                })

                logger.info(f"Copied reference material: {filename}")

            except Exception as e:
                logger.error(f"Failed to copy reference material {filename}: {e}")

        # Generate README.md
        readme_content = self._generate_context_readme(readme_sections)
        readme_path = context_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        logger.info(f"✅ Created context directory with {len(references)} reference materials")

    def _generate_context_readme(self, sections: Dict[str, List[Dict]]) -> str:
        """Generate README.md for context directory"""
        lines = [
            "# Reference Materials",
            "",
            "This directory contains reference materials used during prototype generation.",
            ""
        ]

        section_titles = {
            'skills': 'Skills',
            'diagrams': 'Diagrams',
            'documents': 'Documents',
            'code-samples': 'Code Samples',
            'workflows': 'Workflows'
        }

        for key, title in section_titles.items():
            items = sections.get(key, [])
            if not items:
                continue

            lines.append(f"## {title}")
            for item in items:
                filename = item['filename']
                note = item['note']
                if note:
                    lines.append(f"- **{filename}** - {note}")
                else:
                    lines.append(f"- **{filename}**")
            lines.append("")

        lines.append("---")
        lines.append("*These materials were provided during IdeaBot and referenced throughout ProtoBot workflow*")
        lines.append("")

        return '\n'.join(lines)

    async def write_artifacts(self, project_id: str, output_dir: str) -> Dict[str, Any]:
        """
        Write all code, infrastructure, and communications artifacts to disk.

        Args:
            project_id: Project identifier
            output_dir: Output directory path

        Returns:
            Dict with file count and file list
        """
        # Get all artifacts from ProtoBot session
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise ValueError("ProtoBot session not found")

        # Collect all artifacts
        all_artifacts = []

        # Code artifacts
        if protobot_session.get('step6_code_artifacts'):
            all_artifacts.extend(protobot_session['step6_code_artifacts'])

        # Infrastructure artifacts
        if protobot_session.get('step6_infra_artifacts'):
            all_artifacts.extend(protobot_session['step6_infra_artifacts'])

        # Communications artifacts
        if protobot_session.get('step6_comms_artifacts'):
            comms = protobot_session['step6_comms_artifacts']

            # Email
            if comms.get('email'):
                all_artifacts.append({
                    'filename': 'handoff-email.eml',
                    'content': comms['email'],
                    'type': 'communication',
                    'language': None
                })

            # Calendar invite
            if comms.get('calendar'):
                all_artifacts.append({
                    'filename': 'handoff-meeting.ics',
                    'content': comms['calendar'],
                    'type': 'communication',
                    'language': None
                })

            # Blog post
            if comms.get('blog'):
                all_artifacts.append({
                    'filename': 'blog-post.md',
                    'content': comms['blog'],
                    'type': 'communication',
                    'language': 'markdown'
                })

        if not all_artifacts:
            raise ValueError("No artifacts found to write")

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create context directory and copy reference materials
        await self._setup_context_directory(project_id, output_path)

        # Write each file
        written_files = []
        for artifact in all_artifacts:
            filename = artifact.get('filename', 'unknown.txt')
            content = artifact.get('content', '')

            # Handle nested paths
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                written_files.append({
                    'filename': filename,
                    'path': str(file_path),
                    'size': len(content)
                })

                logger.info(f"Wrote {filename} ({len(content)} bytes)")

            except Exception as e:
                logger.error(f"Failed to write {filename}: {e}")
                raise

        # Write manifest file
        manifest = {
            'project_id': project_id,
            'generated_at': datetime.utcnow().isoformat(),
            'file_count': len(written_files),
            'files': written_files
        }

        manifest_path = output_path / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"✅ Wrote {len(written_files)} files to {output_dir}")

        return {
            'file_count': len(written_files),
            'files': written_files,
            'manifest_path': str(manifest_path)
        }

    async def generate_patch(self, project_id: str, commit_message: str) -> Dict[str, str]:
        """
        Generate git patch file from code artifacts.

        Args:
            project_id: Project identifier
            commit_message: Git commit message

        Returns:
            Dict with patch file path
        """
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise ValueError("ProtoBot session not found")

        code_artifacts = protobot_session.get('step6_code_artifacts', [])
        if not code_artifacts:
            raise ValueError("No code artifacts found")

        # Create patches directory
        patches_dir = Path('output') / 'patches'
        patches_dir.mkdir(parents=True, exist_ok=True)

        # Generate patch file
        patch_filename = f"{project_id}.patch"
        patch_path = patches_dir / patch_filename

        # Build patch content
        patch_lines = []
        patch_lines.append(f"From: ProtoBot <protobot@redhat.com>")
        patch_lines.append(f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}")
        patch_lines.append(f"Subject: [PATCH] {commit_message}")
        patch_lines.append("")
        patch_lines.append(commit_message)
        patch_lines.append("")
        patch_lines.append("---")
        patch_lines.append(f" {len(code_artifacts)} files changed")
        patch_lines.append("")

        # Add each file as a diff
        for artifact in code_artifacts:
            filename = artifact.get('filename', 'unknown.txt')
            content = artifact.get('content', '')

            patch_lines.append(f"diff --git a/{filename} b/{filename}")
            patch_lines.append("new file mode 100644")
            patch_lines.append("index 0000000..0000000")
            patch_lines.append(f"--- /dev/null")
            patch_lines.append(f"+++ b/{filename}")
            patch_lines.append("@@ -0,0 +1,{} @@".format(len(content.split('\n'))))

            # Add content with + prefix
            for line in content.split('\n'):
                patch_lines.append(f"+{line}")

            patch_lines.append("")

        patch_lines.append("--")
        patch_lines.append("2.43.0")
        patch_lines.append("")

        # Write patch file
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(patch_lines))

        logger.info(f"✅ Generated patch file: {patch_path}")

        return {
            'patch_file': str(patch_path),
            'commit_message': commit_message
        }

    async def send_communications(self, project_id: str, recipients: str) -> Dict[str, Any]:
        """
        Send handoff email and calendar invite.

        In mock mode, writes files to disk instead of sending.
        In production mode, would actually send emails.

        Args:
            project_id: Project identifier
            recipients: Comma-separated email addresses

        Returns:
            Dict with send status
        """
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise ValueError("ProtoBot session not found")

        comms = protobot_session.get('step6_comms_artifacts')
        if not comms:
            raise ValueError("Communications artifacts not found")

        # Parse recipients
        recipient_list = [r.strip() for r in recipients.split(',')]

        if settings.is_mock_mode():
            # Mock mode: Write to disk instead of sending
            comms_dir = Path('output') / project_id / 'communications'
            comms_dir.mkdir(parents=True, exist_ok=True)

            # Write email
            email_path = comms_dir / 'handoff-email.eml'
            with open(email_path, 'w', encoding='utf-8') as f:
                f.write(f"To: {', '.join(recipient_list)}\n")
                f.write(comms.get('email', ''))

            # Write calendar invite
            calendar_path = comms_dir / 'handoff-meeting.ics'
            with open(calendar_path, 'w', encoding='utf-8') as f:
                f.write(comms.get('calendar', ''))

            logger.info(f"📧 [MOCK] Communications written to {comms_dir}")

            return {
                'sent': True,
                'mock_mode': True,
                'email_path': str(email_path),
                'calendar_path': str(calendar_path),
                'recipients': recipient_list
            }
        else:
            # Production mode: Actually send emails
            # TODO: Implement real email sending via SMTP or API
            logger.warning("Production email sending not yet implemented")

            return {
                'sent': False,
                'mock_mode': False,
                'message': 'Production email sending not implemented'
            }

    async def update_jira(self, project_id: str, jira_ticket: str) -> Dict[str, str]:
        """
        Update JIRA ticket with handoff information.

        In mock mode, writes update to file.
        In production mode, would use JIRA API.

        Args:
            project_id: Project identifier
            jira_ticket: JIRA ticket key (e.g., OCTO-123)

        Returns:
            Dict with JIRA URL
        """
        protobot_session = await get_protobot_session(project_id)
        ideabot_session = await get_ideabot_session(project_id)
        project = await get_project(project_id)

        # Build JIRA comment
        comment = f"""**ProtoBot Handoff Complete**

Project: {project.get('name', 'Unknown')}
Status: Ready for Transfer

**Artifacts Generated:**
- Code artifacts: {len(protobot_session.get('step6_code_artifacts', []))} files
- Infrastructure manifests: {len(protobot_session.get('step6_infra_artifacts', []))} files
- Communications: Email, Calendar, Blog Post

**Next Steps:**
1. Review artifacts in output/{project_id}/
2. Apply git patch: {project_id}.patch
3. Attend handoff meeting (calendar invite sent)
4. Review technical blueprint

**Catcher Team:**
- PM: {ideabot_session['answers'].get('q7_catcher_pm', 'N/A')}
- EM: {ideabot_session['answers'].get('q8_catcher_em', 'N/A')}
- TL: {ideabot_session['answers'].get('q9_catcher_tl', 'N/A')}

Repository: https://github.com/redhat-et/{project_id}
"""

        if settings.is_mock_mode():
            # Mock mode: Write to file
            jira_dir = Path('output') / project_id / 'jira'
            jira_dir.mkdir(parents=True, exist_ok=True)

            jira_path = jira_dir / f'{jira_ticket}_update.txt'
            with open(jira_path, 'w', encoding='utf-8') as f:
                f.write(f"JIRA Ticket: {jira_ticket}\n")
                f.write(f"Updated: {datetime.utcnow().isoformat()}\n")
                f.write("\n")
                f.write(comment)

            logger.info(f"📋 [MOCK] JIRA update written to {jira_path}")

            return {
                'jira_url': f'https://issues.redhat.com/browse/{jira_ticket}',
                'mock_mode': True,
                'update_path': str(jira_path)
            }
        else:
            # Production mode: Use JIRA API
            # TODO: Implement real JIRA API integration
            logger.warning("Production JIRA API not yet implemented")

            return {
                'jira_url': f'https://issues.redhat.com/browse/{jira_ticket}',
                'mock_mode': False,
                'message': 'Production JIRA API not implemented'
            }


# ============================================================================
# Global Instance
# ============================================================================

# Singleton instance
file_executor = FileExecutor()
