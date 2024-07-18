# Locust UI

The Locust UI is used for viewing stats, reports, and information on your current Locust test from the browser.

## Locust UI as a Library

The Locust UI may be extended to fit your needs. If you only need limited extensibility, you may do so in your Locustfile, see the [extend_web_ui example](https://github.com/locustio/locust/blob/master/examples/extend_web_ui.py). 

However, you may want to further extend certain functionalities. To do so, you may replace the default Locust UI with your own React application. Start by installing the locust-ui in your React application:
```sh
npm install locust-ui
```
or
```sh
yarn add locust-ui
```

## Usage

```js
import LocustUi from "locust-ui";

function App() {
    return (
        <LocustUi<"content-length", "content_length">
            extendedTabs={[
                {
                    title: "Content Length",
                    key: "content-length",
                },
            ]}
            extendedTables={[
                {
                    key: "content-length",
                    structure: [
                        { key: "name", title: "Name" },
                        { key: "content_length", title: "Total content length" },
                    ],
                },
            ]}
            extendedReports={[
                {
                    href: "/content-length/csv",
                    title: "Download content length statistics CSV",
                },
            ]}
            extendedStats={[
                {
                    key: "content-length",
                    data: [{ name: "/", safeName: "/", content_length: "123" }],
                },
            ]}
        />
    )
}
```

For Locust to be able to pass data to your React frontend, place the following script tag in your html template file:
```html
<script>
    window.templateArgs = {{ template_args|tojson }}
</script>
```

Lastly, you must configure Locust to point to your own React build output. To achieve this, you can use the flag `--build-path` and provide the **absolute** path to your build directory.

```sh
locust -f locust.py --build-path /home/user/custom-webui/dist
```

For more on configuring Locust see [the Locust docs](https://docs.locust.io/en/stable/configuration.html).

### Customizing Tabs
By default, the extended tabs will display the provided data in a table. However you may choose to render any React component in the tab:
```js
import { IRootState } from "locust-webui";
import { useSelector } from "react-redux";

function MyCustomTab() {
    const extendedStats = useSelector(
        ({ ui: { extendedStats } }: IRootState) => extendedStats
    );

    return <div>{JSON.stringify(extendedStats)}</div>;
}

const extendedTabs = {[
    {
        title: "Content Length",
        key: "content-length",
        component: MyCustomTab
    },
]};

function App() {
    return (
        <LocustUi extendedTabs={extendedTabs} />
    )
}
```

The `tabs` prop allows for complete control of which tabs are rendered. You can then customize which base tabs are shown or where your new tab should be placed:
```js
import LocustUi, { baseTabs } from "locust-ui";

const tabs = [...baseTabs];
tabs.splice(2, 0, {
  title: "Custom Tab",
  key: "custom-tab",
  component: MyCustomTab,
});

function App() {
    return (
        <LocustUi tabs={tabs} />
    )
}
```

### API
**Tab**
```js
{
    title: string; // **Required** Any string for display purposes
    key: string; // **Required** Programatic key used in extendedTabs to find corresponding stats and tables
    component: // **Optional** React component to render
    shouldDisplayTab: // **Optional** Function provided with Locust redux state to output boolean
}
```
**Extended Stat**
```js
{
    key: string; // **Required** Programatic key that must correspond to a tab key
    data: {
        [key: string]: string; // The key must have a corresponding entry in the extended table structure. The value corresponds to the data to be displayed
    }[];
}
```
**Extended Table**
```js
{
    key: string; // **Required** Programatic key that must correspond to a tab key
    structure: {
        key: string; // **Required** key that must correspond to a key in the extended stat data object
        title: string; // **Required** Corresponds to the title of the column in the table
    }[]
}
```
**Locust UI**
```js
// Provide the types for your extended tab and stat keys to get helpful type hints
<LocustUI<ExtendedTabType, StatKey>
    extendedTabs={/* Optional array of extended tabs */}
    extendedTables={/* Optional array of extended tables */}
    extendedReports={/* Optional array of extended reports */}
    extendedStats={/* Optional array of extended stats */}
    tabs={/* Optional array of tabs that will take precedence over extendedTabs */}
/>
```



