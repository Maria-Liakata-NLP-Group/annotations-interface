import argparse
import sys
import os
import pickle
from app.models import (
    User,
    ClientAnnotationLabel,
    TherapistAnnotationLabel,
    DyadAnnotationLabel,
)
from app import create_app
from sqlalchemy import desc


def cli(args=None):
    """Command line interface for exporting annotations"""

    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, help="User to export annotations for")
    parser.add_argument("--dataset", type=str, help="Dataset to export annotations for")
    args = parser.parse_args(args)
    export_annotations(args.user, args.dataset)


def organize_annotations(annotations_list, annotation_label_model):
    """Organize annotations into a dictionary"""

    parent_labels = annotation_label_model.find_parent_labels()
    organized_annotations = []
    for annotation in annotations_list:
        # first deal with the dialog events
        dialog_turns = annotation.dialog_turns.all()
        dialog_events = []
        for dialog_turn in dialog_turns:
            dialog_events.extend(
                [
                    (
                        dialog_event.event_n,
                        dialog_event.event_speaker,
                        dialog_event.event_plaintext,
                    )
                    for dialog_event in dialog_turn.dialog_events.all()
                ]
            )
        my_dict = {"dialog_events": dialog_events}
        my_dict["timestamp"] = annotation.timestamp
        my_dict["summary_comment"] = annotation.comment_summary
        # labels
        associations = annotation.annotation_label_associations.all()
        main_labels = [
            assoc.label for assoc in associations if assoc.is_additional == False
        ]
        additional_labels = [
            assoc.label for assoc in associations if assoc.is_additional == True
        ]
        # scales
        associations = annotation.annotation_scale_associations.all()
        main_scales = [
            assoc.scale for assoc in associations if assoc.is_additional == False
        ]
        additional_scales = [
            assoc.scale for assoc in associations if assoc.is_additional == True
        ]
        # evidence
        main_evidence = annotation.evidence.filter_by(is_additional=False).all()
        additional_evidence = annotation.evidence.filter_by(is_additional=True).all()
        # comments
        main_comments = annotation.annotation_comments.filter_by(
            is_additional=False
        ).all()
        additional_comments = annotation.annotation_comments.filter_by(
            is_additional=True
        ).all()
        for parent_label in parent_labels:
            my_dict[parent_label.label] = {}
            my_dict[parent_label.label]["main"] = {}
            my_dict[parent_label.label]["additional"] = {}
            label_depth = annotation_label_model.find_parent_label_depth(parent_label)
            # main labels
            labels = [parent_label]
            for level in range(label_depth):
                child_label = [
                    label for label in main_labels if label.parent == labels[-1]
                ]
                if child_label:
                    labels.append(child_label[0])
            labels = labels[1:]
            labels = [label.label for label in labels]
            my_dict[parent_label.label]["main"]["labels"] = labels
            # additional labels
            labels = [parent_label]
            for level in range(label_depth):
                child_label = [
                    label for label in additional_labels if label.parent == labels[-1]
                ]
                if child_label:
                    labels.append(child_label[0])
            labels = labels[1:]
            labels = [label.label for label in labels]
            my_dict[parent_label.label]["additional"]["labels"] = labels
            # main scales
            scales = []
            for scale in main_scales:
                if scale.label == parent_label:
                    scales.append((scale.scale_title, scale.scale_level))
            my_dict[parent_label.label]["main"]["scales"] = scales
            # additional scales
            scales = []
            for scale in additional_scales:
                if scale.label == parent_label:
                    scales.append((scale.scale_title, scale.scale_level))
            my_dict[parent_label.label]["additional"]["scales"] = scales
            # main evidence
            evidence = []
            for ev in main_evidence:
                if ev.label == parent_label:
                    evidence.append(ev.dialog_event.event_n)
            my_dict[parent_label.label]["main"]["evidence"] = evidence
            # additional evidence
            evidence = []
            for ev in additional_evidence:
                if ev.label == parent_label:
                    evidence.append(ev.dialog_event.event_n)
            my_dict[parent_label.label]["additional"]["evidence"] = evidence
            # main comments
            comments = []
            for comment in main_comments:
                if comment.label == parent_label:
                    comments.append(comment.comment)
            my_dict[parent_label.label]["main"]["comments"] = comments
            # additional comments
            comments = []
            for comment in additional_comments:
                if comment.label == parent_label:
                    comments.append(comment.comment)
            my_dict[parent_label.label]["additional"]["comments"] = comments
        organized_annotations.append(my_dict)
    return organized_annotations


def save_annotations(
    user,
    dataset,
    annotations_client,
    annotations_therapist,
    annotations_dyad,
):
    # check that a folder called "exported_annotations" exists
    # if not, create one
    if not os.path.exists("exported_annotations"):
        os.makedirs("exported_annotations")
    full_path = os.path.join("exported_annotations", user)
    # check that a folder with the user's name exists
    # if not, create one
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    full_path = os.path.join(full_path, dataset)
    # check that a folder with the dataset's name exists
    # if not, create one
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    # save client annotations as pickle
    with open(os.path.join(full_path, "client_annotations.pkl"), "wb") as f:
        pickle.dump(annotations_client, f)
    # save therapist annotations as pickle
    with open(os.path.join(full_path, "therapist_annotations.pkl"), "wb") as f:
        pickle.dump(annotations_therapist, f)
    # save dyad annotations as pickle
    with open(os.path.join(full_path, "dyad_annotations.pkl"), "wb") as f:
        pickle.dump(annotations_dyad, f)


def export_annotations(user, dataset):
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=user).first()
        if not user:
            raise ValueError("User not found")
        dataset = user.datasets.filter_by(name=dataset).first()
        if not dataset:
            raise ValueError("Dataset not found")

        # find all dialog turns associated with the dataset
        dialog_turns = dataset.dialog_turns.all()
        # sort the dialog turns by dialog turn number
        dialog_turns = sorted(dialog_turns, key=lambda x: x.dialog_turn_n)
        annotations_client = []
        annotations_therapist = []
        annotations_dyad = []
        # for each dialog turn get the annotation with the latest timestamp
        for dialog_turn in dialog_turns:
            annotations_client.append(
                dialog_turn.annotations_client.filter_by(id_user=user.id)
                .order_by(desc("timestamp"))
                .first()
            )
            annotations_therapist.append(
                dialog_turn.annotations_therapist.filter_by(id_user=user.id)
                .order_by(desc("timestamp"))
                .first()
            )
            annotations_dyad.append(
                dialog_turn.annotations_dyad.filter_by(id_user=user.id)
                .order_by(desc("timestamp"))
                .first()
            )

        # keep the unique annotations, maintaining the order and removing the None values
        # the annotations are ordered by dialog turn number
        annotations_client = list(dict.fromkeys(annotations_client))
        annotations_therapist = list(dict.fromkeys(annotations_therapist))
        annotations_dyad = list(dict.fromkeys(annotations_dyad))
        # drop the None values
        annotations_client = [x for x in annotations_client if x is not None]
        annotations_therapist = [x for x in annotations_therapist if x is not None]
        annotations_dyad = [x for x in annotations_dyad if x is not None]

        # client annotations
        client_annotation_label = ClientAnnotationLabel()
        annotations_client = organize_annotations(
            annotations_client, client_annotation_label
        )

        # therapist annotations
        therapist_annotation_label = TherapistAnnotationLabel()
        annotations_therapist = organize_annotations(
            annotations_therapist, therapist_annotation_label
        )

        # dyad annotations
        dyad_annotation_label = DyadAnnotationLabel()
        annotations_dyad = organize_annotations(annotations_dyad, dyad_annotation_label)

    save_annotations(
        user.username,
        dataset.name,
        annotations_client,
        annotations_therapist,
        annotations_dyad,
    )


if __name__ == "__main__":
    cli()
