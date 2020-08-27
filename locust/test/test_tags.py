from locust import TaskSet, User, task, tag
from locust.user.task import filter_tasks_by_tags
from locust.env import Environment
from .testcases import LocustTestCase


class TestTags(LocustTestCase):
    def test_tagging(self):
        @tag("tag1")
        @task
        def tagged():
            pass

        self.assertIn("locust_tag_set", dir(tagged))
        self.assertEqual(set(["tag1"]), tagged.locust_tag_set)

        @tag("tag2", "tag3")
        @task
        def tagged_multiple_args():
            pass

        self.assertIn("locust_tag_set", dir(tagged_multiple_args))
        self.assertEqual(set(["tag2", "tag3"]), tagged_multiple_args.locust_tag_set)

        @tag("tag4")
        @tag("tag5")
        @task
        def tagged_multiple_times():
            pass

        self.assertIn("locust_tag_set", dir(tagged_multiple_times))
        self.assertEqual(set(["tag4", "tag5"]), tagged_multiple_times.locust_tag_set)

    def test_tagging_taskset(self):
        @tag("taskset")
        @task
        class MyTaskSet(TaskSet):
            @task
            def tagged(self):
                pass

            @tag("task")
            @task
            def tagged_again(self):
                pass

            @tag("taskset2")
            @task
            class NestedTaskSet(TaskSet):
                @task
                def nested_task(self):
                    pass

        # when tagging taskset, its tasks receive the tag
        self.assertIn("locust_tag_set", dir(MyTaskSet.tagged))
        self.assertEqual(set(["taskset"]), MyTaskSet.tagged.locust_tag_set)

        # tagging inner task receives both
        self.assertIn("locust_tag_set", dir(MyTaskSet.tagged_again))
        self.assertEqual(set(["taskset", "task"]), MyTaskSet.tagged_again.locust_tag_set)

        # when tagging nested taskset, its tasks receives both
        self.assertIn("locust_tag_set", dir(MyTaskSet.NestedTaskSet.nested_task))
        self.assertEqual(set(["taskset", "taskset2"]), MyTaskSet.NestedTaskSet.nested_task.locust_tag_set)

    def test_tagging_without_args_fails(self):
        @task
        def dummy_task(self):
            pass

        # task is tagged without parens
        self.assertRaises(ValueError, lambda: tag(dummy_task))

        # task is tagged with empty parens
        self.assertRaises(ValueError, lambda: tag()(dummy_task))

    def test_including_tags(self):
        class MyTaskSet(TaskSet):
            @tag("include this", "other tag")
            @task
            def included(self):
                pass

            @tag("dont include this", "other tag")
            @task
            def not_included(self):
                pass

            @task
            def dont_include_this_either(self):
                pass

        self.assertListEqual(
            MyTaskSet.tasks, [MyTaskSet.included, MyTaskSet.not_included, MyTaskSet.dont_include_this_either]
        )

        filter_tasks_by_tags(MyTaskSet, tags=set(["include this"]))
        self.assertListEqual(MyTaskSet.tasks, [MyTaskSet.included])

    def test_excluding_tags(self):
        class MyTaskSet(TaskSet):
            @tag("exclude this", "other tag")
            @task
            def excluded(self):
                pass

            @tag("dont exclude this", "other tag")
            @task
            def not_excluded(self):
                pass

            @task
            def dont_exclude_this_either(self):
                pass

        self.assertListEqual(
            MyTaskSet.tasks, [MyTaskSet.excluded, MyTaskSet.not_excluded, MyTaskSet.dont_exclude_this_either]
        )

        filter_tasks_by_tags(MyTaskSet, exclude_tags=set(["exclude this"]))
        self.assertListEqual(MyTaskSet.tasks, [MyTaskSet.not_excluded, MyTaskSet.dont_exclude_this_either])

    def test_including_and_excluding(self):
        class MyTaskSet(TaskSet):
            @task
            def not_included_or_excluded(self):
                pass

            @tag("included")
            @task
            def included(self):
                pass

            @tag("excluded")
            @task
            def excluded(self):
                pass

            @tag("included", "excluded")
            @task
            def included_and_excluded(self):
                pass

        filter_tasks_by_tags(MyTaskSet, tags=set(["included"]), exclude_tags=set(["excluded"]))
        self.assertListEqual(MyTaskSet.tasks, [MyTaskSet.included])

    def test_including_tasksets(self):
        class MyTaskSet(TaskSet):
            @task
            class MixedNestedTaskSet(TaskSet):
                @tag("included")
                @task
                def included(self):
                    pass

                @task
                def not_included(self):
                    pass

            @tag("included")
            @task
            class TaggedNestedTaskSet(TaskSet):
                @task
                def included(self):
                    pass

            @task
            class NormalNestedTaskSet(TaskSet):
                @task
                def not_included(self):
                    pass

        filter_tasks_by_tags(MyTaskSet, tags=set(["included"]))
        self.assertListEqual(MyTaskSet.tasks, [MyTaskSet.MixedNestedTaskSet, MyTaskSet.TaggedNestedTaskSet])
        self.assertListEqual(MyTaskSet.MixedNestedTaskSet.tasks, [MyTaskSet.MixedNestedTaskSet.included])

    def test_excluding_tasksets(self):
        class MyTaskSet(TaskSet):
            @task
            class MixedNestedTaskSet(TaskSet):
                @tag("excluded")
                @task
                def excluded(self):
                    pass

                @task
                def not_excluded(self):
                    pass

            @task
            class ExcludedNestedTaskSet(TaskSet):
                @tag("excluded")
                @task
                def excluded(self):
                    pass

            @tag("excluded")
            @task
            class TaggedNestedTaskSet(TaskSet):
                @task
                def excluded(self):
                    pass

            @task
            class NormalNestedTaskSet(TaskSet):
                @task
                def not_excluded(self):
                    pass

        filter_tasks_by_tags(MyTaskSet, exclude_tags=set(["excluded"]))
        self.assertListEqual(MyTaskSet.tasks, [MyTaskSet.MixedNestedTaskSet, MyTaskSet.NormalNestedTaskSet])
        self.assertListEqual(MyTaskSet.MixedNestedTaskSet.tasks, [MyTaskSet.MixedNestedTaskSet.not_excluded])

    def test_including_tags_with_weights(self):
        class MyTaskSet(TaskSet):
            @tag("included")
            @task(2)
            def include_twice(self):
                pass

            @tag("included")
            @task(3)
            def include_3_times(self):
                pass

            @tag("dont include this")
            @task(4)
            def dont_include_4_times(self):
                pass

            @task(5)
            def dont_include_5_times(self):
                pass

        self.assertListEqual(
            MyTaskSet.tasks,
            [
                MyTaskSet.include_twice,
                MyTaskSet.include_twice,
                MyTaskSet.include_3_times,
                MyTaskSet.include_3_times,
                MyTaskSet.include_3_times,
                MyTaskSet.dont_include_4_times,
                MyTaskSet.dont_include_4_times,
                MyTaskSet.dont_include_4_times,
                MyTaskSet.dont_include_4_times,
                MyTaskSet.dont_include_5_times,
                MyTaskSet.dont_include_5_times,
                MyTaskSet.dont_include_5_times,
                MyTaskSet.dont_include_5_times,
                MyTaskSet.dont_include_5_times,
            ],
        )

        filter_tasks_by_tags(MyTaskSet, tags=set(["included"]))

        self.assertListEqual(
            MyTaskSet.tasks,
            [
                MyTaskSet.include_twice,
                MyTaskSet.include_twice,
                MyTaskSet.include_3_times,
                MyTaskSet.include_3_times,
                MyTaskSet.include_3_times,
            ],
        )

    def test_excluding_tags_with_weights(self):
        class MyTaskSet(TaskSet):
            @tag("dont exclude this")
            @task(2)
            def dont_exclude_twice(self):
                pass

            @task(3)
            def dont_exclude_3_times(self):
                pass

            @tag("excluded")
            @task(4)
            def exclude_4_times(self):
                pass

            @tag("excluded")
            @task(5)
            def exclude_5_times(self):
                pass

        self.assertListEqual(
            MyTaskSet.tasks,
            [
                MyTaskSet.dont_exclude_twice,
                MyTaskSet.dont_exclude_twice,
                MyTaskSet.dont_exclude_3_times,
                MyTaskSet.dont_exclude_3_times,
                MyTaskSet.dont_exclude_3_times,
                MyTaskSet.exclude_4_times,
                MyTaskSet.exclude_4_times,
                MyTaskSet.exclude_4_times,
                MyTaskSet.exclude_4_times,
                MyTaskSet.exclude_5_times,
                MyTaskSet.exclude_5_times,
                MyTaskSet.exclude_5_times,
                MyTaskSet.exclude_5_times,
                MyTaskSet.exclude_5_times,
            ],
        )

        filter_tasks_by_tags(MyTaskSet, exclude_tags=set(["excluded"]))

        self.assertListEqual(
            MyTaskSet.tasks,
            [
                MyTaskSet.dont_exclude_twice,
                MyTaskSet.dont_exclude_twice,
                MyTaskSet.dont_exclude_3_times,
                MyTaskSet.dont_exclude_3_times,
                MyTaskSet.dont_exclude_3_times,
            ],
        )

    def test_tagged_tasks_shared_across_tasksets(self):
        @tag("tagged")
        def shared_task():
            pass

        def untagged_shared_task():
            pass

        @tag("tagged")
        class SharedTaskSet(TaskSet):
            @task
            def inner_task(self):
                pass

        class IncludeTaskSet(TaskSet):
            tasks = [shared_task, untagged_shared_task, SharedTaskSet]

        class ExcludeTaskSet(TaskSet):
            tasks = [shared_task, untagged_shared_task, SharedTaskSet]

        filter_tasks_by_tags(IncludeTaskSet, tags=set(["tagged"]))

        self.assertListEqual(IncludeTaskSet.tasks, [shared_task, SharedTaskSet])
        self.assertListEqual(IncludeTaskSet.tasks[1].tasks, [SharedTaskSet.inner_task])

        filter_tasks_by_tags(ExcludeTaskSet, exclude_tags=set(["tagged"]))

        self.assertListEqual(ExcludeTaskSet.tasks, [untagged_shared_task])

    def test_include_tags_under_user(self):
        class MyUser(User):
            @tag("include this")
            @task
            def included(self):
                pass

            @tag("dont include this")
            @task
            def not_included(self):
                pass

            @task
            def dont_include_this_either(self):
                pass

        filter_tasks_by_tags(MyUser, tags=set(["include this"]))

        self.assertListEqual(MyUser.tasks, [MyUser.included])

    def test_exclude_tags_under_user(self):
        class MyUser(User):
            @tag("exclude this")
            @task
            def excluded(self):
                pass

            @tag("dont exclude this")
            @task
            def not_excluded(self):
                pass

            @task
            def dont_exclude_this_either(self):
                pass

        filter_tasks_by_tags(MyUser, exclude_tags=set(["exclude this"]))

        self.assertListEqual(MyUser.tasks, [MyUser.not_excluded, MyUser.dont_exclude_this_either])

    def test_env_include_tags(self):
        class MyTaskSet(TaskSet):
            @tag("include this")
            @task
            def included(self):
                pass

            @tag("dont include this")
            @task
            def not_included(self):
                pass

            @task
            def dont_include_this_either(self):
                pass

        class MyUser(User):
            tasks = [MyTaskSet]

        env = Environment(user_classes=[MyUser], tags=["include this"])
        env._filter_tasks_by_tags()

        self.assertListEqual(MyUser.tasks, [MyTaskSet])
        self.assertListEqual(MyUser.tasks[0].tasks, [MyTaskSet.included])

    def test_env_exclude_tags(self):
        class MyTaskSet(User):
            @tag("exclude this")
            @task
            def excluded(self):
                pass

            @tag("dont exclude this")
            @task
            def not_excluded(self):
                pass

            @task
            def dont_exclude_this_either(self):
                pass

        class MyUser(User):
            tasks = [MyTaskSet]

        env = Environment(user_classes=[MyUser], exclude_tags=["exclude this"])
        env._filter_tasks_by_tags()

        self.assertListEqual(MyUser.tasks, [MyTaskSet])
        self.assertListEqual(MyUser.tasks[0].tasks, [MyTaskSet.not_excluded, MyTaskSet.dont_exclude_this_either])
